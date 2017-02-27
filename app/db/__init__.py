import logging
import peewee as p
from functools import wraps
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import model_to_dict
from app.utils import config


DB = PooledMySQLDatabase(config.MYSQL_DB_NAME,
                         host=config.MYSQL_HOST,
                         port=config.MYSQL_PORT,
                         user=config.MYSQL_USER,
                         passwd=config.MYSQL_PASSWORD,
                         ssl=config.MYSQL_SSL,
                         max_connections=config.MYSQL_MAX_CONNECTIONS,
                         stale_timeout=config.MYSQL_STALE_TIMEOUT)


if config.PEEWEE_LOGGING:
    # Print all queries to stderr.
    logger = logging.getLogger('peewee')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())


class BaseModel(p.Model):
    class Meta:
        database = DB

    def to_dict(self, **kwargs):
        return model_to_dict(self, **kwargs)


class lazy_property(object):
    """
    meant to be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    """
    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value


def retry_on_deadlock(func, max_attempts=5):
    @wraps(func)
    def wrapper(*args, **kwargs):
        attempts = 0
        while attempts < max_attempts:
            try:
                with DB.atomic():
                    return func(*args, **kwargs)
            except p.OperationalError as e:
                attempts += 1
        raise
    return wrapper


# Import models here. Import order is important
# ---------------------------------------------
from .user import CachedUser
from .user import User

# Update tables array when adding a new model. This is used to create all tables in order (primarily in testing).
# Order matters for resolving foreign keys on table creation.
DB_TABLES = [User]
