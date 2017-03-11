import falcon
from app import endpoints, middleware
from app.utils import config

# Basic Initialization
falcon_app = falcon.API(middleware=[
    middleware.Headers(),
    middleware.DBConnect(),
    middleware.SerializeResponseToJSON(),
    middleware.ErrorContext()
])

# Error handling
falcon_app.add_error_handler(Exception, middleware.report_exception)

# Routes
for endpoint in endpoints.Endpoint.__subclasses__():
    falcon_app.add_route(endpoint.route, endpoint)
