from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """POST /api/sportoase/login - Development login endpoint"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Benutzername und Passwort erforderlich'}, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'user': {
                    'username': user.username,
                    'is_staff': user.is_staff,
                    'permissions': list(user.get_all_permissions())
                }
            })
        else:
            return JsonResponse({'error': 'Ungültige Anmeldedaten'}, status=401)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def logout_view(request):
    """POST /api/sportoase/logout - Logout endpoint"""
    logout(request)
    return JsonResponse({'success': True})


@require_http_methods(["GET"])
def check_auth(request):
    """GET /api/sportoase/check-auth - Check authentication status"""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'username': request.user.username,
                'is_staff': request.user.is_staff,
                'permissions': list(request.user.get_all_permissions())
            }
        })
    return JsonResponse({'authenticated': False})
