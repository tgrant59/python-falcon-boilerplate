import datetime
import falcon
from app.db import User
from app.core import user_core
from app.utils import cache, config, constants, encryption, errors


def login(email, password, remember_me):
    try:
        user = User.get(User.email == email)
    except User.DoesNotExist:
        raise errors.AuthenticationError(title="User Not Found", description="No user with that email address")
    if encryption.encrypt_password(password, salt=user.password) != user.password:
        raise errors.AuthenticationError(title="Incorrect Password", description="The given password is incorrect")
    return _new_session(user, remember_me=remember_me)


def logout(user, session_id):
    cache.remove_session(user, session_id)
    return {
        "name": constants.AUTH_COOKIE_NAME,
        "value": session_id,
        "domain": config.AUTH_COOKIE_DOMAIN,
        "path": config.AUTH_COOKIE_PATH,
        "expires": datetime.datetime(1970, 01, 01),  # Cookie should be discarded immediately
        "http_only": config.AUTH_COOKIE_HTTP_ONLY,
        "secure": config.AUTH_COOKIE_SECURE
    }


def signup(email, first_name, last_name, password):
    hashed_password = encryption.encrypt_password(password)
    try:
        User.get(User.email == email)
        raise falcon.HTTPBadRequest("Email Already In Use", "The entered email is already an account")
    except User.DoesNotExist:
        new_user = user_core.create_user(email, hashed_password, first_name, last_name)
        return _new_session(new_user)


def _new_session(user, remember_me=False):
    session_id = encryption.generate_random_token()
    csrf_token = encryption.generate_random_token()
    if remember_me:
        expires = datetime.datetime.utcnow() + constants.AUTH_COOKIE_EXPIRY_DELTA
    else:
        expires = None
    cache.set_session(user, session_id)
    session_cookie = {
        "name": constants.AUTH_COOKIE_NAME,
        "value": session_id,
        "domain": config.AUTH_COOKIE_DOMAIN,
        "path": config.AUTH_COOKIE_PATH,
        "expires": expires,
        "http_only": config.AUTH_COOKIE_HTTP_ONLY,
        "secure": config.AUTH_COOKIE_SECURE

    }
    csrf_cookie = {
        "name": constants.AUTH_CSRF_COOKIE_NAME,
        "value": csrf_token,
        "domain": config.AUTH_COOKIE_DOMAIN,
        "path": config.AUTH_COOKIE_PATH,
        "expires": expires,
        "http_only": constants.AUTH_CSRF_COOKIE_HTTP_ONLY,
        "secure": config.AUTH_COOKIE_SECURE
    }
    return session_cookie, csrf_cookie
