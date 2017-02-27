import json
import datetime
import falcon
import pytest
from app.db import User
from app.core import auth_core
from app.utils import cache, encryption, errors


def test_login(user):
    wrong_pass = "wrongpass"
    right_pass = "password123"
    fake_email = "fake@example.com"
    with pytest.raises(errors.AuthenticationError):
        auth_core.login(user.email, wrong_pass, False)  # Test wrong password
    with pytest.raises(errors.AuthenticationError):
        auth_core.login(fake_email, right_pass, False)  # Test no user found
    session_cookie, csrf_cookie = auth_core.login(user.email, right_pass, False)
    assert session_cookie is not None
    assert csrf_cookie is not None
    session_user = json.loads(cache.get_user_from_session(session_cookie["value"]))
    assert session_user["id"] == user.id
    # Test expiry dates with and without remember me
    assert session_cookie["expires"] is None
    assert csrf_cookie["expires"] is None
    remember_session_cookie, remember_csrf_cookie = auth_core.login(user.email, right_pass, True)
    remember_session_user = json.loads(cache.get_user_from_session(remember_session_cookie["value"]))
    assert remember_session_user["id"] == user.id
    assert remember_session_cookie is not None
    assert isinstance(remember_session_cookie["expires"], datetime.datetime)
    assert remember_session_cookie["expires"] > datetime.datetime.today()
    assert remember_csrf_cookie is not None
    assert isinstance(remember_csrf_cookie["expires"], datetime.datetime)
    assert remember_csrf_cookie["expires"] > datetime.datetime.today()


def test_logout(user):
    right_pass = "password123"
    session_cookie, csrf_cookie = auth_core.login(user.email, right_pass, False)
    auth_core.logout(user, session_id=session_cookie["value"])
    assert cache.get_user_from_session(session_cookie["value"]) is None


def test_signup(user):
    email = "user2@example.com"
    first_name = "Connor"
    last_name = "McDavid"
    password = "anotherpassword"
    session_cookie, csrf_cookie = auth_core.signup(email, first_name, last_name, password)
    db_user = User.get(User.email == email)
    assert db_user.password == encryption.encrypt_password(password, db_user.password)
    session_user = json.loads(cache.get_user_from_session(session_cookie["value"]))
    assert session_user["id"] == db_user.id
    with pytest.raises(falcon.HTTPBadRequest):
        auth_core.signup("user@example.com", first_name, last_name, password)  # Email in use


def test__new_session(user):
    cookie_keys = ["name", "value", "domain", "path", "expires", "http_only", "secure"]
    session_cookie, csrf_cookie = auth_core._new_session(user, remember_me=False)
    session_user = json.loads(cache.get_user_from_session(session_cookie["value"]))
    assert session_user["id"] == user.id
    remember_session_cookie, remember_csrf_cookie = auth_core._new_session(user, remember_me=True)
    for key in cookie_keys:
        assert key in session_cookie
        assert key in csrf_cookie
        assert key in remember_session_cookie
        assert key in remember_csrf_cookie
    assert session_cookie["expires"] is None
    assert csrf_cookie["expires"] is None
    assert isinstance(remember_session_cookie["expires"], datetime.datetime)
    assert remember_session_cookie["expires"] > datetime.datetime.today()
    assert isinstance(remember_csrf_cookie["expires"], datetime.datetime)
    assert remember_csrf_cookie["expires"] > datetime.datetime.today()
