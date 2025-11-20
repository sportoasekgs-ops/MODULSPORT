from django.contrib.auth.models import User
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class IServAuthMiddleware:
    """
    Middleware for IServ authentication integration.
    
    When deployed in IServ, this middleware handles authentication by:
    1. Reading user information from IServ's request headers/session
    2. Creating or updating Django User objects based on IServ user data
    3. Syncing IServ permissions to Django permissions
    
    For development/testing outside IServ, it falls back to standard Django auth.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'ISERV_AUTH_ENABLED', False)
    
    def __call__(self, request):
        if self.enabled and not request.user.is_authenticated:
            self._authenticate_iserv_user(request)
        
        response = self.get_response(request)
        return response
    
    def _authenticate_iserv_user(self, request):
        """
        Authenticate user based on IServ session/headers.
        
        IServ typically provides user information via:
        - HTTP_X_ISERV_USER: Username
        - HTTP_X_ISERV_EMAIL: Email address
        - HTTP_X_ISERV_FIRSTNAME: First name
        - HTTP_X_ISERV_LASTNAME: Last name
        - HTTP_X_ISERV_GROUPS: Comma-separated list of groups
        
        Adjust header names based on your IServ configuration.
        """
        username = request.META.get('HTTP_X_ISERV_USER')
        
        if not username:
            return
        
        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': request.META.get('HTTP_X_ISERV_EMAIL', ''),
                    'first_name': request.META.get('HTTP_X_ISERV_FIRSTNAME', ''),
                    'last_name': request.META.get('HTTP_X_ISERV_LASTNAME', ''),
                }
            )
            
            if not created:
                user.email = request.META.get('HTTP_X_ISERV_EMAIL', user.email)
                user.first_name = request.META.get('HTTP_X_ISERV_FIRSTNAME', user.first_name)
                user.last_name = request.META.get('HTTP_X_ISERV_LASTNAME', user.last_name)
                user.save()
            
            self._sync_permissions(user, request)
            
            from django.contrib.auth import login
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            logger.info(f"IServ user authenticated: {username}")
            
        except Exception as e:
            logger.error(f"IServ authentication error: {str(e)}")
    
    def _sync_permissions(self, user, request):
        """
        Sync IServ groups/permissions to Django user permissions.
        
        Maps IServ groups to Django permissions:
        - Teachers -> sportoase.user permission
        - Admins -> sportoase.admin permission
        """
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        iserv_groups = request.META.get('HTTP_X_ISERV_GROUPS', '').split(',')
        iserv_groups = [g.strip().lower() for g in iserv_groups if g.strip()]
        
        try:
            content_type = ContentType.objects.get(app_label='backend', model='booking')
            
            if 'lehrer' in iserv_groups or 'teachers' in iserv_groups:
                perm, _ = Permission.objects.get_or_create(
                    codename='user',
                    name='Can use SportOase',
                    content_type=content_type
                )
                user.user_permissions.add(perm)
            
            if 'admin' in iserv_groups or 'administrators' in iserv_groups:
                perm, _ = Permission.objects.get_or_create(
                    codename='admin',
                    name='Can administer SportOase',
                    content_type=content_type
                )
                user.user_permissions.add(perm)
                
                admin_perm, _ = Permission.objects.get_or_create(
                    codename='user',
                    name='Can use SportOase',
                    content_type=content_type
                )
                user.user_permissions.add(admin_perm)
            
        except Exception as e:
            logger.error(f"Error syncing permissions: {str(e)}")
