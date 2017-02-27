from app.endpoints import Endpoint


class HealthCheckEndpoint(Endpoint):
    route = "/v1/health-check"

    def on_get(self, req, resp):
        # TODO: Consider adding checks making sure the resources powering the application are reachable
        # e.g. MySQL, Redis, Mongo
        resp.data = {}
