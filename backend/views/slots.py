from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from backend.services.booking_service import BookingService
from backend.models import TimeSlot
import json


@require_http_methods(["GET"])
def get_available_slots(request):
    """GET /api/sportoase/slots - Gibt verfügbare Slots zurück"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentifizierung erforderlich")
    
    if not request.user.has_perm("sportoase.user"):
        return HttpResponseForbidden("Keine Berechtigung")
    
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Datum erforderlich'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Ungültiges Datumsformat (YYYY-MM-DD erwartet)'}, status=400)
    
    slots = BookingService.get_available_slots(date, request.user)
    
    return JsonResponse({
        'success': True,
        'date': date_str,
        'slots': slots
    })


@require_http_methods(["GET"])
def get_week_overview(request):
    """GET /api/sportoase/slots/week - Gibt Übersicht für eine Woche zurück"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentifizierung erforderlich")
    
    if not request.user.has_perm("sportoase.user"):
        return HttpResponseForbidden("Keine Berechtigung")
    
    start_date_str = request.GET.get('start_date')
    if not start_date_str:
        today = datetime.now().date()
        start_date = today - timedelta(days=today.weekday())
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Ungültiges Datumsformat'}, status=400)
    
    week_data = []
    for i in range(5):
        date = start_date + timedelta(days=i)
        slots = BookingService.get_available_slots(date)
        week_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'weekday': date.strftime('%A'),
            'slots': slots
        })
    
    return JsonResponse({
        'success': True,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'week_data': week_data
    })


@require_http_methods(["GET"])
def get_timeslots(request):
    """GET /api/sportoase/timeslots - Gibt alle konfigurierten Zeitslots zurück"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Authentifizierung erforderlich")
    
    timeslots = TimeSlot.objects.all().order_by('weekday', 'period')
    
    return JsonResponse({
        'success': True,
        'timeslots': [{
            'id': ts.id,
            'weekday': ts.weekday,
            'period': ts.period,
            'label': ts.label,
            'start_time': ts.start_time.strftime('%H:%M'),
            'end_time': ts.end_time.strftime('%H:%M'),
            'max_students': ts.max_students,
        } for ts in timeslots]
    })
