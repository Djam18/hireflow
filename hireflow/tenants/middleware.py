from .models import Company


class TenantMiddleware:
    """Attach the current company tenant to the request based on user profile.

    Simple approach: each user belongs to one company via their profile.
    Querysets are then filtered by request.company in views.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.company = None
        if request.user.is_authenticated:
            try:
                request.company = request.user.profile.company
            except Exception:
                pass
        return self.get_response(request)
