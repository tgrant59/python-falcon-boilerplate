import traceback
import falcon
from app.db import DB
from app.async import mailer
from app.utils import config, errors, helpers, reporting


class Headers(object):

    def process_response(self, req, resp, resource):
        resp.set_headers(config.RESPONSE_HEADERS)


class DBConnect(object):

    def process_request(self, req, resp):
        DB.connect()

    def process_response(self, req, resp, resource):
        if not DB.is_closed():
            DB.close()


class SerializeResponseToJSON(object):

    def process_response(self, req, resp, resource):
        data_type = type(resp.data)
        if data_type == str:  # Check str first (Assuming JSON-formatted string)
            data = resp.data
        elif data_type == dict:  # Check dict second (most common type)
            data = helpers.jsondumps(resp.data)
        elif data_type == unicode:
            data = resp.data.encode("utf8")  # Assuming JSON-formatted unicode
        elif resp.data is None:
            data = "{}"
        else:
            raise errors.ReturnTypeError(str(data_type))
        resp.data = ")]}',\n" + data


class ErrorContext(object):

    def process_request(self, req, resp):
        reporting.add_request_context(req)

    def process_response(self, req, resp, resource):
        reporting.clear_context()


def email_on_error(ex, req, resp, params):
    if not issubclass(ex.__class__, falcon.HTTPError) or isinstance(ex, errors.ServerError):
        mailer.error.delay(traceback.format_exc())
    raise
