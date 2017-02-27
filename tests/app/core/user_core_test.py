import falcon
import pytest
from app.db import DB, User
from app.db.documents import UserSettings
from app.core import user_core
from app.utils import cache, constants, encryption, payment

RANDOM_TOKEN = "notsorandomtoken"


def generate_random_token_patch():
    return RANDOM_TOKEN


def test_create_user(monkeypatch):
    def create_customer_patch(_, __):
        return {"id": encryption.generate_random_token(32)}
    monkeypatch.setattr(payment, "create_customer", create_customer_patch)
    email = "user@example.com"
    password = "password123"
    first_name = "Nikita"
    last_name = "Zaitsev"
    hashed_pw = encryption.encrypt_password(password)
    with DB.atomic() as txn:
        new_user = user_core.create_user(email, hashed_pw, first_name, last_name)
        assert new_user.email == email
        assert encryption.encrypt_password(password, new_user.password) == new_user.password
        assert new_user.full_name == first_name + " " + last_name
        assert new_user.role == constants.USER_ROLE_UNVERIFIED
        assert isinstance(new_user.settings, dict)
        UserSettings.delete(new_user._settings_id)
        txn.rollback()


def test_change_name(user):
    user_core.change_name(user, "Mats", "Sundin")
    db_user = User.get(User.id == user.id)
    assert db_user.first_name == "Mats"
    assert db_user.last_name == "Sundin"
    assert db_user.full_name == "Mats Sundin"


def test_change_password(user):
    old_pw = "password123"
    new_pw = "newpassword456"
    user_core.change_password(user, old_pw, new_pw)
    db_user = User.get(User.id == user.id)
    assert encryption.encrypt_password(old_pw, db_user.password) != db_user.password
    assert encryption.encrypt_password(new_pw, db_user.password) == db_user.password


def test_forgot_password(user, monkeypatch):
    monkeypatch.setattr(encryption, "generate_random_token", generate_random_token_patch)
    user_core.forgot_password(user.email)
    assert cache.get_user_id_by_password_reset_token(RANDOM_TOKEN) == user.id
    assert cache.RDB.ttl("forgot_password:" + RANDOM_TOKEN) <= constants.REDIS_EXPIRY_PASSWORD_RESET
    # Test user with that email not found
    with pytest.raises(falcon.HTTPBadRequest):
        user_core.forgot_password("fake@example.com")


def test_reset_password(user, monkeypatch):
    monkeypatch.setattr(encryption, "generate_random_token", generate_random_token_patch)
    new_pw = "newpassword456"
    user_core.forgot_password(user.email)
    user_core.reset_password(new_pw, RANDOM_TOKEN)
    db_user = User.get(User.id == user.id)
    assert encryption.encrypt_password(new_pw, db_user.password) == db_user.password
    # Test token is made invalid
    assert cache.get_user_id_by_password_reset_token(RANDOM_TOKEN) is None
    # Test bad token
    with pytest.raises(falcon.HTTPBadRequest):
        user_core.reset_password(new_pw, "badtoken")


def test_new_verification_email(user, monkeypatch):
    monkeypatch.setattr(encryption, "generate_random_token", generate_random_token_patch)
    user_core.new_verification_email(user)
    assert cache.get_user_id_by_email_verification_token(RANDOM_TOKEN) == user.id
    assert cache.RDB.ttl("email_verification:" + RANDOM_TOKEN) <= constants.REDIS_EXPIRY_EMAIL_VERIFICATION


def test_verify_email(user, monkeypatch):
    monkeypatch.setattr(encryption, "generate_random_token", generate_random_token_patch)
    user_core.new_verification_email(user)
    user_core.verify_email(RANDOM_TOKEN)
    db_user = User.get(User.id == user.id)
    assert db_user.role == constants.USER_ROLE_UNPAID
    # Test token is made invalid
    assert cache.get_user_id_by_email_verification_token(RANDOM_TOKEN) is None
    # Test bad token
    with pytest.raises(falcon.HTTPBadRequest):
        user_core.verify_email("badtoken")


def test_unsubscribe(user):
    user_core.unsubscribe(user.id, user.email)
    assert user.settings["notifications"]["unsubscribe"] is True
    with pytest.raises(falcon.HTTPBadRequest):
        user_core.unsubscribe(5, "fake@example.com")
