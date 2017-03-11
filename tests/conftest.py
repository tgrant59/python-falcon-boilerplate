import os
import sys
import pytest
import redis
from peewee import MySQLDatabase
sys.path.insert(0, os.path.abspath('.'))
from app import db
from app.utils import cache, config, documents


@pytest.fixture(autouse=True)
def setup_task(celery_worker):
    # Start DB Transaction
    with db.DB.atomic() as txn:
        yield
        txn.rollback()
    # Clear Redis
    cache.RDB.flushdb()
    # Drop MongoDB
    documents.MONGO_CLIENT.drop_database(os.environ["MONGO_TEST_DB"])


@pytest.fixture(scope='session')
def setup_pytest():
    # Monkeypatching MySQL, MongoDB and Redis to use testing databases
    db.DB = MySQLDatabase(os.environ["MYSQL_TEST_DB"],
                          host=config.MYSQL_HOST,
                          port=config.MYSQL_PORT,
                          user=os.environ["MYSQL_TEST_USER"],
                          passwd=os.environ["MYSQL_TEST_PASSWORD"],
                          ssl=config.MYSQL_SSL)
    for model in db.DB_TABLES:
        model.create_table()
    documents.MDB = documents.MONGO_CLIENT[os.environ["MONGO_TEST_DB"]]
    cache.RDB = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=os.environ["REDIS_TEST_DB"])
    yield
    # Dropping or flushing testing databases
    cache.RDB.flushdb()
    documents.MONGO_CLIENT.drop_database(os.environ["MONGO_TEST_DB"])
    db.DB.drop_tables(db.DB_TABLES, safe=True)
