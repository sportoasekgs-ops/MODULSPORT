from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def get_csrf_token(request):
    """GET /api/sportoase/csrf - Returns CSRF token for the frontend"""
    return JsonResponse({
        'csrfToken': get_token(request)
    })
