import voluptuous as v
from app.endpoints import Endpoint, load_validated_form
from app.core import error_core


class ErrorEndpoint(Endpoint):
    route = "/v1/error"

    def on_post(self, req, resp):
        validate = v.Schema({
            "error": v.All(unicode, v.Length(min=1, max=10240))
        })
        form_data = load_validated_form(req, validate)
        error_core.report_error(form_data["error"])
