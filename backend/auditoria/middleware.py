from .auditlog_context import set_request

class AuditlogMiddleware:
    """
    Guarda el request actual en thread-local
    para que las señales puedan acceder a user/ip/UA.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_request(request)
        return self.get_response(request)
