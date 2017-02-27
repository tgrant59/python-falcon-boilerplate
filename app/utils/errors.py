import falcon


class TimeoutException(Exception):
    pass


class AuthenticationError(falcon.HTTPUnauthorized):
    def __init__(self, title=None, description=None):
        super(AuthenticationError, self).__init__(title=title or "Authentication Error",
                                                  description=description or "Incorrect or missing credentials",
                                                  challenges=["token"])


class AuthorizationError(falcon.HTTPForbidden):
    def __init__(self, title=None, description=None):
        super(AuthorizationError, self).__init__(title=title or "Authorization Error",
                                                 description=description or "User does not have access to this endpoint")


class ServerError(falcon.HTTPInternalServerError):
    def __init__(self, title=None, description=None):
        super(ServerError, self).__init__(title=title or "Internal Server Error",
                                          description=description or "Something went seriously, seriously wrong...")


class ReturnTypeError(falcon.HTTPInternalServerError):
    def __init__(self, return_type):
        super(ReturnTypeError, self).__init__(title="Return Type Error",
                                              description="The returned type is invalid: " + return_type)
