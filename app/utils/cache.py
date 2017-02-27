import redis
from app.utils import config, constants, helpers

RDB = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, password=config.REDIS_PASSWORD, db=config.REDIS_DB)


# ---------- Sessions -----------
def set_session(user, session_id):
    session_key = "session:{0}".format(session_id)
    session_data = helpers.jsondumps(user.to_dict())
    pipe = RDB.pipeline()
    pipe.set(session_key, session_data)
    pipe.expire(session_key, constants.AUTH_COOKIE_EXPIRY_SECONDS)
    pipe.sadd("user_sessions:{0}".format(user.id), str(session_id))
    pipe.execute()


def get_user_from_session(session_id):
    key = "session:{0}".format(session_id)
    pipe = RDB.pipeline()
    pipe.get(key)
    pipe.expire(key, constants.AUTH_COOKIE_EXPIRY_SECONDS)
    cached_user = pipe.execute()[0]
    return cached_user


def remove_session(user, session_id):
    pipe = RDB.pipeline()
    pipe.delete("session:{0}".format(session_id))
    pipe.srem("user_sessions:{0}".format(user.id), session_id)
    pipe.execute()


def update_all_sessions(user):
    session_list_key = "user_sessions:{0}".format(user.id)
    session_ids = RDB.smembers(session_list_key)
    if session_ids:
        user_data = helpers.jsondumps(user.to_dict())
        pipe = RDB.pipeline()
        for session_id in session_ids:
            key = "session:{0}".format(session_id)
            if RDB.exists(key):
                pipe.set(key, user_data)
            else:
                pipe.srem(session_list_key, session_id)
        pipe.execute()


def remove_all_sessions(user):
    session_list_key = "user_sessions:{0}".format(user.id)
    session_keys = RDB.smembers(session_list_key)
    if session_keys:
        pipe = RDB.pipeline()
        for session_key in session_keys:
            pipe.delete("session:{0}".format(session_key))
        pipe.delete(session_list_key)
        pipe.execute()


# -------- Email Verification Tokens --------
def set_email_verification_token(user, verification_token):
    key = "email_verification:{0}".format(verification_token)
    RDB.setex(key, user.id, constants.REDIS_EXPIRY_EMAIL_VERIFICATION)


def get_user_id_by_email_verification_token(verification_token):
    user_id_str = RDB.get("email_verification:{0}".format(verification_token))
    try:
        return int(user_id_str)
    except TypeError:
        return None


def remove_email_verification_token(verification_token):
    RDB.delete("email_verification:{0}".format(verification_token))


# -------- Password Reset Tokens ---------
def set_password_reset_token(user, reset_token):
    key = "forgot_password:{0}".format(reset_token)
    RDB.setex(key, user.id, constants.REDIS_EXPIRY_PASSWORD_RESET)


def get_user_id_by_password_reset_token(reset_token):
    user_id_str = RDB.get("forgot_password:{0}".format(reset_token))
    try:
        return int(user_id_str)
    except TypeError:
        return None


def remove_password_reset_token(reset_token):
    RDB.delete("forgot_password:{0}".format(reset_token))
