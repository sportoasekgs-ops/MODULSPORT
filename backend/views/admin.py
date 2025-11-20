from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from datetime import datetime
from backend.services.booking_service import BookingService
from backend.models import BlockedSlot, Notification
import json


@require_http_methods(["POST"])
def block_slot(request):
    """POST /api/sportoase/block-slot - Blockiert einen Slot (Admin only)"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentifizierung erforderlich")
    
    if not request.user.has_perm("sportoase.admin"):
        return HttpResponseForbidden("Nur für Admins")
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Ungültige JSON-Daten'}, status=400)
    
    required_fields = ['date', 'weekday', 'period']
    for field in required_fields:
        if field not in data:
            return JsonResponse({'success': False, 'error': f'Feld "{field}" fehlt'}, status=400)
    
    try:
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Ungültiges Datumsformat'}, status=400)
    
    try:
        blocked = BookingService.block_slot(
            date=date,
            weekday=data['weekday'],
            period=data['period'],
            admin_user=request.user,
            reason=data.get('reason', 'Beratung')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Slot erfolgreich blockiert',
            'blocked_slot': blocked.to_dict()
        })
    
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except PermissionError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Fehler: {str(e)}'}, status=500)


@require_http_methods(["POST"])
def unblock_slot(request):
    """POST /api/sportoase/unblock-slot - Gibt einen Slot frei (Admin only)"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentifizierung erforderlich")
    
    if not request.user.has_perm("sportoase.admin"):
        return HttpResponseForbidden("Nur für Admins")
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Ungültige JSON-Daten'}, status=400)
    
    try:
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Ungültiges Datumsformat'}, status=400)
    
    try:
        BookingService.unblock_slot(date, data['period'], request.user)
        return JsonResponse({
            'success': True,
            'message': 'Slot erfolgreich freigegeben'
        })
    
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=404)
    except PermissionError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Fehler: {str(e)}'}, status=500)


@require_http_methods(["GET"])
def get_blocked_slots(request):
    """GET /api/sportoase/blocked-slots - Gibt alle blockierten Slots zurück"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentifizierung erforderlich")
    
    if not request.user.has_perm("sportoase.admin"):
        return HttpResponseForbidden("Nur für Admins")
    
    blocked_slots = BlockedSlot.objects.all().order_by('-date', 'period')[:100]
    
    return JsonResponse({
        'success': True,
        'blocked_slots': [bs.to_dict() for bs in blocked_slots]
    })


@require_http_methods(["GET"])
def get_notifications(request):
    """GET /api/sportoase/notifications - Gibt Benachrichtigungen zurück"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentifizierung erforderlich")
    
    if not request.user.has_perm("sportoase.admin"):
        return HttpResponseForbidden("Nur für Admins")
    
    unread_only = request.GET.get('unread_only') == 'true'
    
    if unread_only:
        notifications = BookingService.get_unread_notifications()
    else:
        notifications = Notification.objects.all().order_by('-created_at')[:50]
    
    return JsonResponse({
        'success': True,
        'notifications': [n.to_dict() for n in notifications]
    })


@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """POST /api/sportoase/notifications/<id>/mark-read - Markiert Benachrichtigung als gelesen"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentifizierung erforderlich")
    
    if not request.user.has_perm("sportoase.admin"):
        return HttpResponseForbidden("Nur für Admins")
    
    success = BookingService.mark_notification_read(notification_id)
    
    if success:
        return JsonResponse({
            'success': True,
            'message': 'Benachrichtigung als gelesen markiert'
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Benachrichtigung nicht gefunden'
        }, status=404)
