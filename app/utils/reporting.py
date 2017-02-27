import raven
from raven.contrib import celery as raven_celery
from app.utils import config


client = raven.Client(
    dsn=config.SENTRY_DNS,
    release=raven.fetch_git_sha(config.REPO_PATH),
    processors=(
        "raven.processors.SanitizePasswordsProcessor",
        "raven.processors.RemovePostDataProcessor"
    )
)
raven_celery.register_logger_signal(client)
raven_celery.register_signal(client, ignore_expected=True)


def add_user_context(user):
    client.extra_context({
        "user_settings": user.settings
    })
    client.user_context({
        "id": user.id,
        "email": user.email,
        "name": user.full_name,
        "role": user.role,
        "created": user.created
    })


def add_request_context(req):
    client.http_context({
        "url": req.url,
        "method": req.method,
        "query_string": req.query_string,
        "headers": req.headers,
        "cookies": req.cookies
    })


def add_extra_context(context):
    client.extra_context(context)


def clear_context():
    client.context.clear()


def capture_error():
    client.captureException()


def capture_message(message):
    client.captureMessage(message)
