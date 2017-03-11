import traceback
import raven
from raven.contrib import celery as raven_celery
from app.utils import config


if config.ENVIRONMENT == 'production':
    client = raven.Client(
        dsn=config.SENTRY_DNS,
        release=raven.fetch_git_sha(config.REPO_PATH),
        processors=(
            'raven.processors.SanitizePasswordsProcessor',
            'raven.processors.RemovePostDataProcessor'
        )
    )
    raven_celery.register_logger_signal(client)
    raven_celery.register_signal(client, ignore_expected=True)


def add_user_context(user):
    if config.ENVIRONMENT == 'production':
        client.extra_context({
            'user_settings': user.settings
        })
        client.user_context({
            'id': user.id,
            'email': user.email,
            'name': user.full_name,
            'role': user.role,
            'created': user.created
        })


def add_request_context(req):
    if config.ENVIRONMENT == 'production':
        client.http_context({
            'url': req.url,
            'method': req.method,
            'query_string': req.query_string,
            'headers': req.headers,
            'cookies': req.cookies
        })


def add_extra_context(context):
    if config.ENVIRONMENT == 'production':
        client.extra_context(context)


def clear_context():
    if config.ENVIRONMENT == 'production':
        client.context.clear()


def capture_error():
    if config.ENVIRONMENT == 'production':
        client.captureException()
    else:
        traceback.print_exc()


def capture_message(message):
    if config.ENVIRONMENT == 'production':
        client.captureMessage(message)
    else:
        print message
