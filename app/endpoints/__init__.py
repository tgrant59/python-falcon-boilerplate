import json
import falcon
import multipart
import voluptuous
from app.db import CachedUser
from app.utils import cache, constants, errors


class Endpoint(object):
    def on_options(self, req, resp, **kwargs):
        pass


# ----------------------------------------------------------------------------------------------------------------------
#                                                       Hooks
# ----------------------------------------------------------------------------------------------------------------------

# All hooks take the params 'req, resp, resource, and params'
def authenticated(req, resp, resource, params):
    cookies = req.cookies
    if "session-id" not in cookies or "csrf-token" not in cookies:
        raise errors.AuthenticationError
    if not cookies["session-id"] or not cookies["csrf-token"]:
        raise errors.AuthenticationError
    user_str = cache.get_user_from_session(cookies["session-id"])
    if not user_str:
        raise errors.AuthenticationError
    cached_user = CachedUser(json.loads(user_str))
    if hasattr(resource, "roles"):
        if cached_user.role not in resource.roles:
            raise errors.AuthorizationError
    req.context["session_id"] = cookies["session-id"]
    params["user"] = cached_user


# ----------------------------------------------------------------------------------------------------------------------
#                                              Form Retrieval and Validation
# ----------------------------------------------------------------------------------------------------------------------

def load_multipart_form(req, parts):
    boundary = None
    for keyval in req.content_type.split(";"):
        if keyval.strip().startswith("boundary="):
            boundary = keyval.split("=")[1]
    if not boundary:
        raise falcon.HTTPBadRequest("Invalid Multipart Form", "No boundary was found in the content-type header")
    parser = multipart.MultipartParser(req.stream, boundary, content_length=req.content_length or -1)
    form_data = []
    for part in parts:
        try:
            form_data.append(parser.get(part))
        except IndexError:
            raise falcon.HTTPBadRequest("Invalid Form", part + " is a required parameter in the Multipart Form")
    return tuple(form_data)


def load_form(req):
    try:
        return json.load(req.stream)
    except ValueError:
        raise falcon.HTTPBadRequest("Invalid Form", "Malformed or missing JSON")


def validate_form(form_data, validate):
    try:
        return validate(form_data)
    except voluptuous.MultipleInvalid as e:
        err_msg = ""
        for err in e.errors:
            err_msg += str(err) + " | "
        raise falcon.HTTPBadRequest("Invalid Form", err_msg.rstrip(" |"))


def load_validated_form(req, validate):
    form_data = load_form(req)
    return validate_form(form_data, validate)


# ----------------------------------------------------------------------------------------------------------------------
#                                               Validation Helpers
# ----------------------------------------------------------------------------------------------------------------------

def csrf_check(req, csrf_token):
    if constants.AUTH_CSRF_COOKIE_NAME not in req.cookies or req.cookies[constants.AUTH_CSRF_COOKIE_NAME] != csrf_token:
        raise falcon.HTTPBadRequest("Invalid CSRF token", "The CSRF token that accompanied the form input is incorrect")


def coerce_unicode(s):
    try:
        return s.decode(constants.UTF8)
    except AttributeError:
        raise voluptuous.Invalid("expected str to coerce to unicode")


def match(data, key):
    def same(field2):
        try:
            if data[key] != field2:
                raise voluptuous.Invalid("field '{}' does not match".format(key))
        except KeyError:
            raise voluptuous.Invalid("match error with key '{}'".format(key))
    return same
