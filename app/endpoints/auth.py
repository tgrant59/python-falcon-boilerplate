import falcon
import voluptuous as v
from app.core import auth_core
from app.endpoints import Endpoint, authenticated, load_form, validate_form, load_validated_form, match


class AuthLoginEndpoint(Endpoint):
    route = "/v1/auth/login"

    def on_post(self, req, resp):
        validate = v.Schema({
            "email": v.All(unicode, v.Length(min=1, max=256)),
            "password": v.All(unicode, v.Length(min=8, max=256)),
            "remember_me": bool
        }, required=True)
        form_data = load_validated_form(req, validate)
        session_cookie, csrf_cookie = auth_core.login(
            email=form_data["email"],
            password=form_data["password"],
            remember_me=form_data["remember_me"]
        )
        resp.set_cookie(**session_cookie)
        resp.set_cookie(**csrf_cookie)


class AuthLogoutEndpoint(Endpoint):
    route = "/v1/auth/logout"

    @falcon.before(authenticated)
    def on_get(self, req, resp, user=None):
        session_cookie = auth_core.logout(user, req.context["session_id"])
        resp.set_cookie(**session_cookie)


class AuthSignupEndpoint(Endpoint):
    route = "/v1/auth/signup"

    def on_post(self, req, resp):
        form_data = load_form(req)
        validate = v.Schema({
            "email": v.All(unicode, v.Length(min=1, max=256)),
            "first_name": v.All(unicode, v.Length(min=1, max=256)),
            "last_name": v.All(unicode, v.Length(min=1, max=256)),
            "password": v.All(unicode, v.Length(min=8, max=256)),
            "password_confirmation": v.All(unicode, v.Length(min=8, max=256), match(form_data, "password")),
            "terms": True
        }, required=True)
        form_data = validate_form(form_data, validate)
        session_cookie, csrf_cookie = auth_core.signup(
            email=form_data["email"],
            first_name=form_data["first_name"],
            last_name=form_data["last_name"],
            password=form_data["password"]
        )
        resp.set_cookie(**session_cookie)
        resp.set_cookie(**csrf_cookie)
