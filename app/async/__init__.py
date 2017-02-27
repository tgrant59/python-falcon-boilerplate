from functools import wraps
from app.run_celery import celery_app
from app.db import DB


def task(*task_args, **task_kwargs):
    def decorator(func):
        @celery_app.task(*task_args, **task_kwargs)
        @wraps(func)
        def wrapper(*args, **kwargs):
            DB.connect()
            try:
                retval = func(*args, **kwargs)
            finally:
                if not DB.is_closed():
                    DB.close()
            return retval
        return wrapper
    return decorator
