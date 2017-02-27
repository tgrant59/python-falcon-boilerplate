import datetime
import pytz
import falcon
from app.async import mailer
from app.db import User
from app.utils import config, constants, errors, payment


def create_subscription(user, plan, token, coupon_code):
    """
    Make sure you pass this function the db user
    """
    if user.stripe_id is None:
        metadata = {
            "user_id": user.id
        }
        customer = payment.create_customer(user.email, metadata)
        user.stripe_id = customer["id"]
    payment.update_customer_card(user.stripe_id, token["id"])
    sub = payment.create_or_update_subscription(user.stripe_id, plan, user.settings["account"]["had_trial"],
                                                coupon_code)
    trial = False
    if not user.settings["account"]["had_trial"] and plan in config.STRIPE_TRIAL_PLANS:
        trial = True
    user.role = constants.USER_ROLE_PAID
    user.save()
    user.settings["account"]["plan"] = plan
    user.settings["account"]["had_trial"] = True
    user.save_settings()
    mailer.subscription_created.delay(user.id, sub.plan.name, sub.plan.amount, sub.plan.interval, trial=trial)


def update_subscription(user, new_plan):
    """
    Make sure you pass this function the db user
    """
    sub = payment.create_or_update_subscription(user.stripe_id, new_plan, user.settings["account"]["had_trial"])
    user.role = constants.USER_ROLE_PAID
    user.save()
    user.settings["account"]["plan"] = new_plan
    user.save_settings()
    mailer.subscription_updated.delay(user.id, sub.plan.name, sub.plan.amount, sub.plan.interval)


def cancel_subscription(user):
    """
    Make sure you pass this function the db user
    """
    subscription = payment.cancel_subscription(user.stripe_id)
    if subscription and subscription.status != "trialing":
        user.role = constants.USER_ROLE_CANCELLED
        expiry = datetime.datetime.utcfromtimestamp(subscription["current_period_end"])
        user.settings["account"]["expiry"] = expiry
        expiry_eastern = pytz.utc.localize(expiry).astimezone(config.TIMEZONE)
        reminder_datetime = expiry_eastern - datetime.timedelta(days=3)
        mailer.subscription_ending.apply_async(args=[user.id], eta=reminder_datetime)
    else:
        user.role = constants.USER_ROLE_UNPAID
        user.settings["account"]["num_users"] = 1
        mailer.subscription_ended.delay(user.id)
    user.save()
    user.save_settings()


def get_card(user):
    """
    Make sure you pass this function the db user
    """
    if user.stripe_id is None:
        raise falcon.HTTPBadRequest(title="User Not A Customer",
                                    description="The user has no associated payment data associated with it")
    customer = payment.get_customer(user.stripe_id)
    for source in customer["sources"]["data"]:
        if source["id"] == customer["default_source"]:
            today = datetime.datetime.today()
            expired = today.year >= source["exp_year"] and today.month > source["exp_month"]
            return {
                "brand": source["brand"],
                "last4": source["last4"],
                "exp_month": source["exp_month"],
                "exp_year": source["exp_year"],
                "expired": expired
            }
    return {}


def update_card(user, token):
    """
    Make sure you pass this function the db user
    """
    if user.stripe_id is None:
        raise falcon.HTTPBadRequest(title="User Not A Customer",
                                    description="The user has no associated payment data associated with it")
    payment.update_customer_card(user.stripe_id, token["id"])


def get_invoice_history(user, first_invoice, last_invoice):
    """
    Make sure you pass this function the db user
    """
    if user.stripe_id is None:
        return []
    return payment.get_invoice_history(user.stripe_id, first_invoice, last_invoice)


# ----------------------------------------------------------------------------------------------------------------------
#                                               Stripe Webhooks
# ----------------------------------------------------------------------------------------------------------------------

def end_cancelled_subscription(event):
    # Double check Stripe event
    try:
        user = User.get(User.stripe_id == event["data"]["object"]["customer"])
    except User.DoesNotExist:
        raise errors.ServerError(title="Stripe Webhook Error",
                                 description="No user exists with that Stripe customer id")
    subscription = payment.get_subscription(user.stripe_id)
    if not subscription or subscription["status"] != "canceled":
        raise errors.ServerError(title="Stripe Webhook Verification Error",
                                 description="The Stripe event (end_cancelled_subscription) could not be verified")
    # Delete account
    user.role = constants.USER_ROLE_UNPAID
    user.save()
    user.settings["account"]["plan"] = None
    user.settings["account"]["num_users"] = 1
    user.save_settings()
    mailer.subscription_ended.delay(user.id)


def payment_failed_notify_user(event):
    # Double check Stripe event
    try:
        user = User.get(User.stripe_id == event["data"]["object"]["customer"])
    except User.DoesNotExist:
        raise errors.ServerError(title="Stripe Webhook Error",
                                 description="No user exists with that Stripe customer id")
    invoice = payment.get_invoice(event["data"]["object"]["id"])
    if invoice["closed"] or not invoice["attempted"]:
        raise errors.ServerError(title="Stripe Webhook Verification Error",
                                 description="The Stripe event (payment_failed_notify_user) could not be verified")
    # Notify user of failed payment
    if 0 < invoice["attempt_count"] < 4:
        mailer.payment_failed.delay(user.id, invoice["attempt_count"])


def trial_expiring(event):
    # Double check Stripe event
    try:
        user = User.get(User.stripe_id == event["data"]["object"]["customer"])
    except User.DoesNotExist:
        raise errors.ServerError(title="Stripe Webhook Error",
                                 description="No user exists with that Stripe customer id")
    subscription = payment.get_subscription(user.stripe_id)
    if not subscription or subscription["status"] != "trialing":
        raise errors.ServerError(title="Stripe Webhook Verification Error",
                                 description="The Stripe event (trial_expiring) could not be verified")
    mailer.trial_ending.delay(user.id)


def check_coupon_code(coupon_code):
    coupon = payment.retrieve_coupon_code(coupon_code)
    if not coupon or not coupon.valid:
        return None
    return {
        "id": coupon.id,
        "amount_off": coupon.amount_off,
        "percent_off": coupon.percent_off,
        "duration": coupon.duration,
        "duration_in_months": coupon.duration_in_months,
    }
