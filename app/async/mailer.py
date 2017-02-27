import jinja2
from app.async import task
from app.db import User
from app.utils import config, cloud

TEMPLATE_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(config.EMAIL_TEMPLATE_PATH))


class MockUser(object):
    id = 0
    email = "mock@example.com"


def _get_templates(template_name, **template_params):
    template_params["config"] = config
    html_template = TEMPLATE_ENVIRONMENT.get_template(template_name + ".html")
    html = html_template.render(**template_params).encode("utf8")
    text_template = TEMPLATE_ENVIRONMENT.get_template(template_name + ".txt")
    text = text_template.render(**template_params).encode("utf8")
    return html, text


# ----------------------------------------------------------------------------------------------------------------------
#                                               Emails to Users
# ----------------------------------------------------------------------------------------------------------------------

@task(queue="priority")
def welcome(user_id, verification_token):
    user = User.get(User.id == user_id)
    html, text = _get_templates("welcome", user=user, verification_token=verification_token)
    cloud.send_email(
        subject="Welcome!",
        from_address=config.EMAIL_ADMIN_ADDRESS,
        to_address=user.email,
        html=html,
        text=text
    )


@task(queue="priority")
def email_verification(user_id, verification_token):
    user = User.get(User.id == user_id)
    html, text = _get_templates("email_verification", user=user, verification_token=verification_token)
    cloud.send_email(
        subject="Verify your email address!",
        from_address=config.EMAIL_NO_REPLY_ADDRESS,
        to_address=user.email,
        html=html,
        text=text
    )


@task(queue="priority")
def password_reset(user_id, reset_token):
    user = User.get(User.id == user_id)
    html, text = _get_templates("password_reset", user=user, reset_token=reset_token)
    cloud.send_email(
        subject="Your password reset link has arrived",
        from_address=config.EMAIL_NO_REPLY_ADDRESS,
        to_address=user.email,
        html=html,
        text=text
    )


@task(queue="priority")
def payment_failed(user_id, num_attempts):
    user = User.get(User.id == user_id)
    html, text = _get_templates("payment_failed", user=user, num_attempts=num_attempts)
    cloud.send_email(
        subject="ACTION REQUIRED! A payment has failed, your subscription may be cancelled",
        from_address=config.EMAIL_INFO_ADDRESS,
        to_address=user.email,
        html=html,
        text=text
    )


@task(queue="priority")
def subscription_created(user_id, plan, amount, interval, trial=False):
    user = User.get(User.id == user_id)
    html, text = _get_templates("subscription_created", user=user, plan=plan, amount=amount, interval=interval,
                                trial=trial)
    cloud.send_email(
        subject="You're now subscribed! Awesome!",
        from_address=config.EMAIL_INFO_ADDRESS,
        to_address=user.email,
        html=html,
        text=text
    )


@task(queue="priority")
def subscription_updated(user_id, plan, amount, interval):
    user = User.get(User.id == user_id)
    html, text = _get_templates("subscription_updated", user=user, plan=plan, amount=amount, interval=interval)
    cloud.send_email(
        subject="Your subscription has been updated",
        from_address=config.EMAIL_INFO_ADDRESS,
        to_address=user.email,
        html=html,
        text=text
    )


@task(queue="priority")
def subscription_ending(user_id):
    user = User.get(User.id == user_id)
    html, text = _get_templates("subscription_ending", user=user)
    cloud.send_email(
        subject="Your subscription will end soon!",
        from_address=config.EMAIL_INFO_ADDRESS,
        to_address=user.email,
        html=html,
        text=text
    )


@task(queue="priority")
def subscription_ended(user_id):
    user = User.get(User.id == user_id)
    html, text = _get_templates("subscription_ended", user=user)
    cloud.send_email(
        subject="Your subscription has ended",
        from_address=config.EMAIL_INFO_ADDRESS,
        to_address=user.email,
        html=html,
        text=text
    )


@task(queue="priority")
def trial_ending(user_id):
    user = User.get(User.id == user_id)
    html, text = _get_templates("trial_ending", user=user)
    cloud.send_email(
        subject="Your trial is ending soon",
        from_address=config.EMAIL_INFO_ADDRESS,
        to_address=user.email,
        html=html,
        text=text
    )


@task(queue="priority")
def feedback(user_id, given_feedback):
    user = User.get(User.id == user_id)
    mock_user = MockUser()
    html, text = _get_templates("feedback", user=mock_user, feedback_user=user, feedback=given_feedback)
    cloud.send_email(
        subject="Some feedback",
        from_address=config.EMAIL_NO_REPLY_ADDRESS,
        reply_to_address=user.email,
        to_address=config.EMAIL_ADMIN_ADDRESS,
        html=html,
        text=text
    )
