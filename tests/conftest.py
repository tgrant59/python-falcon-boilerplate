import pytest
import redis
from peewee import MySQLDatabase
from app import db
from app.utils import cache, config, documents

MONGO_TEST_DB_NAME = "gretzky-testing"
MYSQL_TEST_DB_NAME = "gretzky-testing"
REDIS_TEST_DB = 2


@pytest.fixture(autouse=True)
def setup_task(celery_worker):
    # Start DB Transaction
    with db.DB.atomic() as txn:
        yield
        txn.rollback()
    # Clear Redis
    cache.RDB.flushdb()
    # Drop MongoDB
    documents.MONGO_CLIENT.drop_database(MONGO_TEST_DB_NAME)


@pytest.fixture(scope="session", autouse=True)
def setup_pytest():
    # Monkeypatching MySQL, MongoDB and Redis to use testing databases
    db.DB = MySQLDatabase(MYSQL_TEST_DB_NAME,
                          host=config.MYSQL_HOST,
                          port=config.MYSQL_PORT,
                          user=config.MYSQL_USER,
                          passwd=config.MYSQL_PASSWORD,
                          ssl=config.MYSQL_SSL)
    for model in db.DB_TABLES:
        model.create_table()
    documents.MDB = documents.MONGO_CLIENT[MONGO_TEST_DB_NAME]
    cache.RDB = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=REDIS_TEST_DB)
    yield
    # Dropping or flushing testing databases
    cache.RDB.flushdb()
    documents.MONGO_CLIENT.drop_database(MONGO_TEST_DB_NAME)
    db.DB.drop_tables(db.DB_TABLES, safe=True)
