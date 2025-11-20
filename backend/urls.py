from django.urls import path
from backend.views import slots, bookings, admin, csrf, auth

app_name = 'sportoase'

urlpatterns = [
    path('csrf', csrf.get_csrf_token, name='csrf_token'),
    path('login', auth.login_view, name='login'),
    path('logout', auth.logout_view, name='logout'),
    path('check-auth', auth.check_auth, name='check_auth'),
    
    path('slots', slots.get_available_slots, name='get_slots'),
    path('slots/week', slots.get_week_overview, name='get_week'),
    path('timeslots', slots.get_timeslots, name='get_timeslots'),
    path('timeslots/<int:timeslot_id>', slots.update_timeslot_label, name='update_timeslot'),
    
    path('book', bookings.create_booking, name='create_booking'),
    path('my-bookings', bookings.get_my_bookings, name='my_bookings'),
    path('bookings', bookings.get_all_bookings, name='all_bookings'),
    path('bookings/<int:booking_id>', bookings.delete_booking, name='delete_booking'),
    
    path('block-slot', admin.block_slot, name='block_slot'),
    path('unblock-slot', admin.unblock_slot, name='unblock_slot'),
    path('blocked-slots', admin.get_blocked_slots, name='blocked_slots'),
    
    path('notifications', admin.get_notifications, name='notifications'),
    path('notifications/<int:notification_id>/mark-read', admin.mark_notification_read, name='mark_notification_read'),
]
