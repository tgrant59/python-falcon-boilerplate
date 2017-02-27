import bcrypt
from os import urandom
from base64 import b64encode
from app.utils import config, constants


def encrypt_password(password, salt=None):
    if salt is None:
        salt = bcrypt.gensalt(config.AUTH_BCRYPT_ROUNDS)
    if isinstance(password, unicode):
        password = password.encode(constants.UTF8)
    if isinstance(salt, unicode):
        salt = salt.encode(constants.UTF8)
    return bcrypt.hashpw(password, salt)


def generate_random_token(length=64):
    return filter(str.isalnum, b64encode(urandom(length)))
