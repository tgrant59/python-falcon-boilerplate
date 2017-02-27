import falcon
import voluptuous as v
from app.core import user_core
from app.endpoints import Endpoint, authenticated, load_validated_form, load_form, validate_form, csrf_check, match
from app.utils import constants


class UserEndpoint(Endpoint):
    route = "/v1/user"

    @falcon.before(authenticated)
    def on_get(self, req, resp, user=None):
        user_dict = user.to_dict()
        del user_dict["password"]
        resp.data = {"user": user_dict}


class UserForgotPasswordEndpoint(Endpoint):
    route = "/v1/user/forgot-password"

    def on_post(self, req, resp):
        validate = v.Schema({
            "email": v.All(unicode, v.Length(min=1, max=256))
        }, required=True)
        form_data = load_validated_form(req, validate)
        user_core.forgot_password(email=form_data["email"])

    def on_put(self, req, resp):
        form_data = load_form(req)
        validate = v.Schema({
            "new_password": v.All(unicode, v.Length(min=8, max=256)),
            "new_password_confirmation": v.All(unicode, v.Length(min=8, max=256), match(form_data, "new_password")),
            "reset_token": v.All(unicode, v.Length(min=1, max=256))
        }, required=True)
        form_data = validate_form(form_data, validate)
        user_core.reset_password(new_password=form_data["new_password"], reset_token=form_data["reset_token"])


class UserNameEndpoint(Endpoint):
    route = "/v1/user/name"
    roles = [constants.USER_ROLE_UNPAID, constants.USER_ROLE_PAID, constants.USER_ROLE_CANCELLED]

    @falcon.before(authenticated)
    def on_put(self, req, resp, user=None):
        validate = v.Schema({
            "new_first_name": v.All(unicode, v.Length(max=256)),
            "new_last_name": v.All(unicode, v.Length(max=256)),
            "csrf_token": v.All(unicode, v.Length(min=1, max=256))
        }, required=True)
        form_data = load_validated_form(req, validate)
        csrf_check(req, form_data["csrf_token"])
        user_core.change_name(user.from_db(), first_name=form_data["new_first_name"], last_name=form_data["new_last_name"])


class UserPasswordEndpoint(Endpoint):
    route = "/v1/user/password"
    roles = [constants.USER_ROLE_UNPAID, constants.USER_ROLE_PAID, constants.USER_ROLE_CANCELLED]

    @falcon.before(authenticated)
    def on_put(self, req, resp, user=None):
        form_data = load_form(req)
        validate = v.Schema({
            "current_password": v.All(unicode, v.Length(min=1, max=256)),
            "new_password": v.All(unicode, v.Length(min=8, max=256)),
            "new_password_confirmation": v.All(unicode, v.Length(min=8, max=256), match(form_data, "new_password")),
            "csrf_token": v.All(unicode, v.Length(min=1, max=256))
        }, required=True)
        form_data = validate_form(form_data, validate)
        user_core.change_password(user.from_db(), current_password=form_data["current_password"],
                                  new_password=form_data["new_password"])


class UserVerifyEmailEndpoint(Endpoint):
    route = "/v1/user/verify-email"

    @falcon.before(authenticated)
    def on_post(self, req, resp, user=None):
        validate = v.Schema({
            "csrf_token": v.All(unicode, v.Length(min=1, max=256))
        }, required=True)
        form_data = load_validated_form(req, validate)
        csrf_check(req, form_data["csrf_token"])
        user_core.new_verification_email(user)

    def on_put(self, req, resp):
        validate = v.Schema({
            "verification_token": v.All(unicode, v.Length(min=1, max=256))
        }, required=True)
        form_data = load_validated_form(req, validate)
        user_core.verify_email(form_data["verification_token"])


class UserFeedbackEndpoint(Endpoint):
    route = "/v1/user/feedback"

    @falcon.before(authenticated)
    def on_post(self, req, resp, user=None):
        validate = v.Schema({
            "feedback": v.All(unicode, v.Length(min=1, max=5120))
        }, required=True)
        form_data = load_validated_form(req, validate)
        user_core.send_feedback(user, form_data["feedback"])


class UserUnsubscribeEndpoint(Endpoint):
    route = "/v1/user/unsubscribe-emails"

    def on_post(self, req, resp):
        validate = v.Schema({
            "user_id": int,
            "email": v.All(unicode, v.Length(min=1, max=256))
        }, required=True)
        form_data = load_validated_form(req, validate)
        user_core.unsubscribe(form_data["user_id"], form_data["email"])
