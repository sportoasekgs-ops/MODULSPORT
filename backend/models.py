from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class TimeSlot(models.Model):
    """Zeitslots mit anpassbaren Namen für verschiedene Perioden"""
    WEEKDAY_CHOICES = [
        ('Mon', 'Montag'),
        ('Tue', 'Dienstag'),
        ('Wed', 'Mittwoch'),
        ('Thu', 'Donnerstag'),
        ('Fri', 'Freitag'),
    ]
    
    weekday = models.CharField(max_length=3, choices=WEEKDAY_CHOICES)
    period = models.IntegerField()
    label = models.CharField(max_length=200)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_students = models.IntegerField(default=200)
    
    class Meta:
        unique_together = ['weekday', 'period']
        ordering = ['weekday', 'period']
        db_table = 'sportoase_timeslots'
    
    def __str__(self):
        return f"{self.get_weekday_display()} - {self.period}. Stunde: {self.label}"


class Booking(models.Model):
    """Buchung einer Sportstunde durch eine Lehrkraft"""
    OFFER_TYPE_CHOICES = [
        ('sport', 'Sport'),
        ('games', 'Spiele'),
        ('outdoor', 'Outdoor'),
        ('other', 'Sonstiges'),
    ]
    
    date = models.DateField(db_index=True)
    weekday = models.CharField(max_length=3)
    period = models.IntegerField()
    
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sportoase_bookings')
    teacher_name = models.CharField(max_length=100)
    teacher_class = models.CharField(max_length=50, blank=True)
    
    students_json = models.TextField()
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)
    offer_label = models.CharField(max_length=100)
    
    calendar_event_id = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', 'period']
        db_table = 'sportoase_bookings'
        indexes = [
            models.Index(fields=['date', 'period']),
            models.Index(fields=['teacher']),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.period}. Stunde: {self.offer_label} ({self.teacher_name})"
    
    @property
    def students(self):
        """Parse students from JSON"""
        try:
            return json.loads(self.students_json)
        except:
            return []
    
    @students.setter
    def students(self, value):
        """Set students as JSON"""
        self.students_json = json.dumps(value, ensure_ascii=False)
    
    @property
    def student_count(self):
        """Count of students in this booking"""
        return len(self.students)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'weekday': self.weekday,
            'period': self.period,
            'teacher_id': self.teacher.id,
            'teacher_name': self.teacher_name,
            'teacher_class': self.teacher_class,
            'teacher_email': self.teacher.email,
            'students': self.students,
            'student_count': self.student_count,
            'offer_type': self.offer_type,
            'offer_label': self.offer_label,
            'calendar_event_id': self.calendar_event_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class BlockedSlot(models.Model):
    """Von Admins blockierte Slots (z.B. für Beratungsgespräche)"""
    date = models.DateField(db_index=True)
    weekday = models.CharField(max_length=3)
    period = models.IntegerField()
    reason = models.CharField(max_length=200, default='Beratung')
    
    blocked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sportoase_blocked_slots')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['date', 'period']
        ordering = ['-date', 'period']
        db_table = 'sportoase_blocked_slots'
        indexes = [
            models.Index(fields=['date', 'period']),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.period}. Stunde: Blockiert ({self.reason})"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'weekday': self.weekday,
            'period': self.period,
            'reason': self.reason,
            'blocked_by': self.blocked_by.username,
            'blocked_by_id': self.blocked_by.id,
            'created_at': self.created_at.isoformat(),
        }


class Notification(models.Model):
    """Benachrichtigungen für Admins über neue Buchungen"""
    NOTIFICATION_TYPES = [
        ('new_booking', 'Neue Buchung'),
        ('booking_updated', 'Buchung aktualisiert'),
        ('booking_deleted', 'Buchung gelöscht'),
        ('slot_blocked', 'Slot blockiert'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=500)
    
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    
    metadata_json = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'sportoase_notifications'
    
    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.message[:50]}"
    
    @property
    def metadata(self):
        """Parse metadata from JSON"""
        if not self.metadata_json:
            return {}
        try:
            return json.loads(self.metadata_json)
        except:
            return {}
    
    @metadata.setter
    def metadata(self, value):
        """Set metadata as JSON"""
        self.metadata_json = json.dumps(value, ensure_ascii=False)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'booking_id': self.booking.id if self.booking else None,
            'notification_type': self.notification_type,
            'message': self.message,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
        }
