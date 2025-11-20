from datetime import datetime, timedelta
from django.db.models import Q, Count, Sum
from django.db import transaction
from backend.models import Booking, TimeSlot, BlockedSlot, Notification
import json


class BookingService:
    """Service-Klasse für Buchungslogik"""
    
    @staticmethod
    def get_available_slots(date, user=None):
        """
        Gibt alle verfügbaren Slots für ein bestimmtes Datum zurück
        
        Args:
            date: datetime.date object
            user: Optional - Django User object für Filterung
        
        Returns:
            List von Dictionaries mit Slot-Informationen
        """
        weekday_map = {
            0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri',
            5: 'Sat', 6: 'Sun'
        }
        weekday = weekday_map.get(date.weekday(), 'Mon')
        
        timeslots = TimeSlot.objects.filter(weekday=weekday).order_by('period')
        
        bookings = Booking.objects.filter(date=date)
        blocked_slots = BlockedSlot.objects.filter(date=date)
        
        booking_dict = {}
        for booking in bookings:
            period = booking.period
            if period not in booking_dict:
                booking_dict[period] = []
            booking_dict[period].append(booking)
        
        blocked_dict = {bs.period: bs for bs in blocked_slots}
        
        result = []
        for slot in timeslots:
            period_bookings = booking_dict.get(slot.period, [])
            student_count = sum(b.student_count for b in period_bookings)
            
            is_blocked = slot.period in blocked_dict
            is_available = not is_blocked and student_count < slot.max_students
            
            slot_info = {
                'period': slot.period,
                'weekday': slot.weekday,
                'label': slot.label,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'max_students': slot.max_students,
                'current_students': student_count,
                'available_spots': max(0, slot.max_students - student_count),
                'is_available': is_available,
                'is_blocked': is_blocked,
                'blocked_reason': blocked_dict[slot.period].reason if is_blocked else None,
                'bookings': [b.to_dict() for b in period_bookings],
            }
            
            result.append(slot_info)
        
        return result
    
    @staticmethod
    def check_student_double_booking(student_name, student_class, date, period, exclude_booking_id=None):
        """
        Prüft, ob ein Schüler bereits für dieses Datum und diese Stunde gebucht ist
        
        Returns:
            Dict mit 'is_booked' (bool) und 'booking_info' (str) oder None
        """
        bookings = Booking.objects.filter(date=date, period=period)
        
        if exclude_booking_id:
            bookings = bookings.exclude(id=exclude_booking_id)
        
        for booking in bookings:
            students = booking.students
            for student in students:
                if (student.get('name', '').strip().lower() == student_name.strip().lower() and 
                    student.get('klasse', '').strip().lower() == student_class.strip().lower()):
                    return {
                        'is_booked': True,
                        'booking_info': f"{student_name} ({student_class}) ist bereits in '{booking.offer_label}' bei {booking.teacher_name} gebucht."
                    }
        
        return {'is_booked': False, 'booking_info': None}
    
    @staticmethod
    @transaction.atomic
    def create_booking(date, weekday, period, teacher, students, offer_type, offer_label, 
                      teacher_name=None, teacher_class=None):
        """
        Erstellt eine neue Buchung
        
        Args:
            date: datetime.date object
            weekday: String ('Mon', 'Tue', etc.)
            period: Integer (1-6)
            teacher: Django User object
            students: List of dicts with student info
            offer_type: String
            offer_label: String
            teacher_name: Optional string
            teacher_class: Optional string
        
        Returns:
            Booking object oder None bei Fehler
        """
        if BlockedSlot.objects.filter(date=date, period=period).exists():
            raise ValueError("Dieser Slot ist blockiert")
        
        for student in students:
            check = BookingService.check_student_double_booking(
                student['name'], student['klasse'], date, period
            )
            if check['is_booked']:
                raise ValueError(check['booking_info'])
        
        booking = Booking.objects.create(
            date=date,
            weekday=weekday,
            period=period,
            teacher=teacher,
            teacher_name=teacher_name or teacher.get_full_name() or teacher.username,
            teacher_class=teacher_class or '',
            students=students,
            offer_type=offer_type,
            offer_label=offer_label,
        )
        
        Notification.objects.create(
            booking=booking,
            notification_type='new_booking',
            message=f"Neue Buchung: {offer_label} von {teacher_name} am {date.strftime('%d.%m.%Y')} - {period}. Stunde",
        )
        
        return booking
    
    @staticmethod
    def get_user_bookings(user, start_date=None, end_date=None):
        """
        Gibt alle Buchungen eines Benutzers zurück
        
        Args:
            user: Django User object
            start_date: Optional datetime.date
            end_date: Optional datetime.date
        
        Returns:
            QuerySet von Booking objects
        """
        bookings = Booking.objects.filter(teacher=user)
        
        if start_date:
            bookings = bookings.filter(date__gte=start_date)
        if end_date:
            bookings = bookings.filter(date__lte=end_date)
        
        return bookings.order_by('-date', 'period')
    
    @staticmethod
    @transaction.atomic
    def block_slot(date, weekday, period, admin_user, reason='Beratung'):
        """
        Blockiert einen Slot (nur für Admins)
        
        Args:
            date: datetime.date object
            weekday: String
            period: Integer
            admin_user: Django User object (Admin)
            reason: String - Grund der Blockierung
        
        Returns:
            BlockedSlot object
        """
        if not admin_user.has_perm('sportoase.admin'):
            raise PermissionError("Nur Admins dürfen Slots blockieren")
        
        if BlockedSlot.objects.filter(date=date, period=period).exists():
            raise ValueError("Slot ist bereits blockiert")
        
        blocked = BlockedSlot.objects.create(
            date=date,
            weekday=weekday,
            period=period,
            reason=reason,
            blocked_by=admin_user,
        )
        
        Notification.objects.create(
            notification_type='slot_blocked',
            message=f"Slot blockiert: {date.strftime('%d.%m.%Y')} - {period}. Stunde ({reason})",
        )
        
        return blocked
    
    @staticmethod
    @transaction.atomic
    def unblock_slot(date, period, admin_user):
        """
        Gibt einen blockierten Slot wieder frei
        
        Args:
            date: datetime.date object
            period: Integer
            admin_user: Django User object (Admin)
        
        Returns:
            True bei Erfolg
        """
        if not admin_user.has_perm('sportoase.admin'):
            raise PermissionError("Nur Admins dürfen Slots entsperren")
        
        blocked = BlockedSlot.objects.filter(date=date, period=period).first()
        if not blocked:
            raise ValueError("Slot ist nicht blockiert")
        
        blocked.delete()
        return True
    
    @staticmethod
    @transaction.atomic
    def delete_booking(booking_id, user):
        """
        Löscht eine Buchung
        
        Args:
            booking_id: Integer
            user: Django User object
        
        Returns:
            True bei Erfolg
        """
        booking = Booking.objects.filter(id=booking_id).first()
        if not booking:
            raise ValueError("Buchung nicht gefunden")
        
        if booking.teacher != user and not user.has_perm('sportoase.admin'):
            raise PermissionError("Keine Berechtigung zum Löschen dieser Buchung")
        
        Notification.objects.create(
            notification_type='booking_deleted',
            message=f"Buchung gelöscht: {booking.offer_label} von {booking.teacher_name} am {booking.date.strftime('%d.%m.%Y')}",
        )
        
        booking.delete()
        return True
    
    @staticmethod
    def get_unread_notifications(limit=50):
        """Gibt ungelesene Benachrichtigungen zurück"""
        return Notification.objects.filter(is_read=False).order_by('-created_at')[:limit]
    
    @staticmethod
    def mark_notification_read(notification_id):
        """Markiert eine Benachrichtigung als gelesen"""
        notification = Notification.objects.filter(id=notification_id).first()
        if notification:
            notification.is_read = True
            notification.read_at = datetime.now()
            notification.save()
            return True
        return False
