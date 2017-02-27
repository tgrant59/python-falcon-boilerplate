import json
import pytest
from app.db import CachedUser
from app.utils import cache, constants


@pytest.fixture
def session(user):
    session_id = "123456789"
    cache.set_session(user, session_id)
    return user, session_id


@pytest.fixture
def two_sessions(user):
    session_id_1 = "123456789"
    session_id_2 = "abcdefghi"
    cache.set_session(user, session_id_1)
    cache.set_session(user, session_id_2)
    return user, session_id_1, session_id_2


# ----------- Cached Session Tests -----------
def test_set_session(user):
    session_id = "123456789"
    key = "session:" + session_id
    user_sessions_key = "user_sessions:" + str(user.id)
    cache.set_session(user, session_id)
    assert cache.RDB.get(key) is not None
    assert 0 <= cache.RDB.ttl(key) <= constants.AUTH_COOKIE_EXPIRY_SECONDS
    assert cache.RDB.sismember(user_sessions_key, session_id)
    cache.remove_all_sessions(user)


def test_get_user_from_session(session):
    user, session_id = session
    user_str = cache.get_user_from_session(session_id)
    assert user_str is not None
    cached_user = CachedUser(json.loads(user_str))
    assert user.id == cached_user.id


def test_remove_session(session):
    user, session_id = session
    key = "session:" + session_id
    user_sessions_key = "user_sessions:" + str(user.id)
    cache.remove_session(user, session_id)
    assert cache.RDB.get(key) is None
    assert not cache.RDB.sismember(user_sessions_key, session_id)


def test_update_all_sessions(two_sessions):
    user, session_id_1, session_id_2 = two_sessions
    user_sessions_key = "user_sessions:" + str(user.id)
    new_first_name = "Auston"
    new_last_name = "Matthews"
    assert cache.RDB.sismember(user_sessions_key, session_id_1)
    assert cache.RDB.sismember(user_sessions_key, session_id_2)
    user.first_name = new_first_name
    user.last_name = new_last_name
    cache.update_all_sessions(user)
    cached_user_1 = CachedUser(json.loads(cache.get_user_from_session(session_id_1)))
    cached_user_2 = CachedUser(json.loads(cache.get_user_from_session(session_id_2)))
    assert cached_user_1.first_name == new_first_name
    assert cached_user_1.last_name == new_last_name
    assert cached_user_2.first_name == new_first_name
    assert cached_user_2.last_name == new_last_name


def test_remove_all_sessions(two_sessions):
    user, session_id_1, session_id_2 = two_sessions
    cache.remove_all_sessions(user)
    assert cache.get_user_from_session(session_id_1) is None
    assert cache.get_user_from_session(session_id_2) is None


# ----------- Cached verification/reset token tests  -----------
def test_set_email_verification_token(user):
    token = "exampletoken"
    key = "email_verification:" + token
    cache.set_email_verification_token(user, token)
    assert cache.RDB.get(key) == str(user.id)
    assert 0 <= cache.RDB.ttl(key) <= constants.REDIS_EXPIRY_EMAIL_VERIFICATION
    cache.RDB.delete(key)


def test_get_user_id_by_email_verification_token(user):
    token = "exampletoken"
    key = "email_verification:" + token
    cache.set_email_verification_token(user, token)
    assert cache.get_user_id_by_email_verification_token(token) == user.id
    assert cache.get_user_id_by_email_verification_token("tokendoesntexist") is None
    cache.RDB.delete(key)


def test_remove_email_verification_token(user):
    token = "exampletoken"
    key = "email_verification:" + token
    cache.set_email_verification_token(user, token)
    cache.remove_email_verification_token(token)
    assert cache.RDB.get(key) is None


def test_set_password_reset_token(user):
    token = "exampletoken"
    key = "forgot_password:" + token
    cache.set_password_reset_token(user, token)
    assert cache.RDB.get(key) == str(user.id)
    assert 0 <= cache.RDB.ttl(key) <= constants.REDIS_EXPIRY_EMAIL_VERIFICATION
    cache.RDB.delete(key)


def test_get_user_id_by_password_reset_token(user):
    token = "exampletoken"
    key = "forgot_password:" + token
    cache.set_password_reset_token(user, token)
    assert cache.get_user_id_by_password_reset_token(token) == user.id
    assert cache.get_user_id_by_password_reset_token("tokendoesntexist") is None
    cache.RDB.delete(key)


def test_remove_password_reset_token(user):
    token = "exampletoken"
    key = "forgot_password:" + token
    cache.set_password_reset_token(user, token)
    cache.remove_password_reset_token(token)
    assert cache.RDB.get(key) is None
