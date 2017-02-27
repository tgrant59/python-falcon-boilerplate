from celery import Celery
from celery.schedules import crontab
from app.utils import config


celery_app = Celery("run_celery")
celery_app.conf.update(**config.CELERY_CONFIG)
celery_app.autodiscover_tasks(lambda: ["app.async"])

# The Celery schedule is in EST/EDT

# Add a representation of each cronjob to the Celery Beat Schedule:
# e.g. 'run_task_every_hour': {
#          'task': 'app.async.cronjobs.task_module.task_name',
#          'schedule': crontab(minute=0)
#      }
celery_app.conf.beat_schedule = {

}
