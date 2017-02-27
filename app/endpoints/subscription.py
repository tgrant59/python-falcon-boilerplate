import falcon
import voluptuous as v
from app.endpoints import Endpoint, authenticated, load_form, load_validated_form, validate_form
from app.core import subscription_core
from app.utils import config, constants


class SubscriptionEndpoint(Endpoint):
    route = "/v1/subscription"
    roles = [constants.USER_ROLE_UNPAID, constants.USER_ROLE_PAID, constants.USER_ROLE_CANCELLED]

    @falcon.before(authenticated)
    def on_post(self, req, resp, user=None):
        validate = v.Schema({
            "plan": v.All(unicode, v.In(config.STRIPE_PLANS.keys())),
            "token": dict,
            v.Optional("coupon_code"): v.All(unicode, v.Length(min=1, max=256))
        }, required=True)
        form_data = load_validated_form(req, validate)
        if "coupon_code" not in form_data:
            form_data["coupon_code"] = None
        subscription_core.create_subscription(user.from_db(), form_data["plan"], form_data["token"],
                                              form_data["coupon_code"])

    @falcon.before(authenticated)
    def on_put(self, req, resp, user=None):
        validate = v.Schema({
            "new_plan": v.All(unicode, v.In(config.STRIPE_PLANS.keys()))
        }, required=True)
        form_data = load_validated_form(req, validate)
        subscription_core.update_subscription(user.from_db(), form_data["new_plan"])

    @falcon.before(authenticated)
    def on_delete(self, req, resp, user=None):
        subscription_core.cancel_subscription(user.from_db())


class SubscriptionCardEndpoint(Endpoint):
    route = "/v1/subscription/card"
    roles = [constants.USER_ROLE_UNPAID, constants.USER_ROLE_PAID, constants.USER_ROLE_CANCELLED]

    @falcon.before(authenticated)
    def on_get(self, req, resp, user=None):
        resp.data = subscription_core.get_card(user.from_db())

    @falcon.before(authenticated)
    def on_post(self, req, resp, user=None):
        token = load_form(req)
        subscription_core.update_card(user.from_db(), token)


class SubscriptionInvoicesEndpoint(Endpoint):
    route = "/v1/subscription/invoices"
    roles = [constants.USER_ROLE_UNPAID, constants.USER_ROLE_PAID, constants.USER_ROLE_CANCELLED]

    @falcon.before(authenticated)
    def on_get(self, req, resp, user=None):
        validate = v.Schema({
            "first_invoice": v.All(str, v.Length(min=1, max=255)),
            "last_invoice": v.All(str, v.Length(min=1, max=255))
        })
        form_data = validate_form(req.params, validate)
        if "first_invoice" not in form_data:
            form_data["first_invoice"] = None
        if "last_invoice" not in form_data:
            form_data["last_invoice"] = None
        invoices = subscription_core.get_invoice_history(user.from_db(), form_data["first_invoice"],
                                                         form_data["last_invoice"])
        resp.data = {"invoices": invoices}


class SubscriptionCouponCodeEndpoint(Endpoint):
    route = "/v1/subscription/coupon-code"
    roles = [constants.USER_ROLE_UNPAID, constants.USER_ROLE_PAID, constants.USER_ROLE_CANCELLED]

    @falcon.before(authenticated)
    def on_post(self, req, resp, user=None):
        validate = v.Schema({
            "coupon_code": v.All(unicode, v.Length(min=1, max=255))
        })
        form_data = load_validated_form(req, validate)
        resp.data = {"coupon": subscription_core.check_coupon_code(form_data["coupon_code"])}


class SubscriptionWebhooksEndpoint(Endpoint):
    route = "/v1/subscription/webhooks"

    def on_post(self, req, resp):
        event = load_form(req)
        if event["type"] == "customer.subscription.deleted":
            subscription_core.end_cancelled_subscription(event)
        elif event["type"] == "customer.subscription.trial_will_end":
            subscription_core.trial_expiring(event)
        elif event["type"] == "invoice.payment_failed":
            subscription_core.payment_failed_notify_user(event)
