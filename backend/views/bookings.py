from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from datetime import datetime
from backend.services.booking_service import BookingService
from backend.models import Booking
import json


@require_http_methods(["POST"])
def create_booking(request):
    """POST /api/sportoase/book - Erstellt eine neue Buchung"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentifizierung erforderlich")
    
    if not request.user.has_perm("sportoase.user"):
        return HttpResponseForbidden("Keine Berechtigung")
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Ungültige JSON-Daten'}, status=400)
    
    required_fields = ['date', 'weekday', 'period', 'students', 'offer_type', 'offer_label']
    for field in required_fields:
        if field not in data:
            return JsonResponse({'success': False, 'error': f'Feld "{field}" fehlt'}, status=400)
    
    try:
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Ungültiges Datumsformat'}, status=400)
    
    try:
        booking = BookingService.create_booking(
            date=date,
            weekday=data['weekday'],
            period=data['period'],
            teacher=request.user,
            students=data['students'],
            offer_type=data['offer_type'],
            offer_label=data['offer_label'],
            teacher_name=data.get('teacher_name'),
            teacher_class=data.get('teacher_class'),
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Buchung erfolgreich erstellt',
            'booking': booking.to_dict()
        })
    
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Fehler beim Erstellen der Buchung: {str(e)}'}, status=500)


@require_http_methods(["GET"])
def get_my_bookings(request):
    """GET /api/sportoase/my-bookings - Gibt die Buchungen des aktuellen Benutzers zurück"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentifizierung erforderlich")
    
    if not request.user.has_perm("sportoase.user"):
        return HttpResponseForbidden("Keine Berechtigung")
    
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    bookings = BookingService.get_user_bookings(request.user, start_date, end_date)
    
    return JsonResponse({
        'success': True,
        'bookings': [b.to_dict() for b in bookings]
    })


@require_http_methods(["DELETE"])
def delete_booking(request, booking_id):
    """DELETE /api/sportoase/bookings/<id> - Löscht eine Buchung"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentifizierung erforderlich")
    
    if not request.user.has_perm("sportoase.user"):
        return HttpResponseForbidden("Keine Berechtigung")
    
    try:
        BookingService.delete_booking(booking_id, request.user)
        return JsonResponse({
            'success': True,
            'message': 'Buchung erfolgreich gelöscht'
        })
    
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=404)
    except PermissionError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Fehler beim Löschen: {str(e)}'}, status=500)


@require_http_methods(["GET"])
def get_all_bookings(request):
    """GET /api/sportoase/bookings - Gibt alle Buchungen zurück (Admin only)"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentifizierung erforderlich")
    
    if not request.user.has_perm("sportoase.admin"):
        return HttpResponseForbidden("Nur für Admins")
    
    date_str = request.GET.get('date')
    
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            bookings = Booking.objects.filter(date=date).order_by('period')
        except ValueError:
            return JsonResponse({'error': 'Ungültiges Datumsformat'}, status=400)
    else:
        bookings = Booking.objects.all().order_by('-date', 'period')[:100]
    
    return JsonResponse({
        'success': True,
        'bookings': [b.to_dict() for b in bookings]
    })
