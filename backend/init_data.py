#!/usr/bin/env python
"""Initialize SportOase database with default timeslots"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, '/home/runner/workspace')

django.setup()

from backend.models import TimeSlot
from datetime import time

def create_timeslots():
    """Create default timeslots for each weekday"""
    periods = [
        {'period': 1, 'label': '1. Stunde', 'start': time(8, 0), 'end': time(8, 45)},
        {'period': 2, 'label': '2. Stunde', 'start': time(8, 50), 'end': time(9, 35)},
        {'period': 3, 'label': '3. Stunde', 'start': time(9, 55), 'end': time(10, 40)},
        {'period': 4, 'label': '4. Stunde', 'start': time(10, 45), 'end': time(11, 30)},
        {'period': 5, 'label': '5. Stunde', 'start': time(11, 50), 'end': time(12, 35)},
        {'period': 6, 'label': '6. Stunde', 'start': time(12, 40), 'end': time(13, 25)},
    ]
    
    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    
    created_count = 0
    for weekday in weekdays:
        for period_data in periods:
            timeslot, created = TimeSlot.objects.get_or_create(
                weekday=weekday,
                period=period_data['period'],
                defaults={
                    'label': period_data['label'],
                    'start_time': period_data['start'],
                    'end_time': period_data['end'],
                    'max_students': 200
                }
            )
            if created:
                created_count += 1
                print(f"✓ Created: {weekday} - {period_data['label']}")
            else:
                print(f"  Exists: {weekday} - {period_data['label']}")
    
    print(f"\n✅ Done! Created {created_count} new timeslots.")
    print(f"Total timeslots in database: {TimeSlot.objects.count()}")

if __name__ == '__main__':
    print("Initializing SportOase timeslots...")
    create_timeslots()
