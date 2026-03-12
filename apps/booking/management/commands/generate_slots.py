"""
Management command: generate_slots

Creates TimeSlot records for the next N days.
~40% of slots are randomly pre-marked as unavailable (simulates existing bookings).

Usage:
    python manage.py generate_slots            # 14 days, plumbing/electrical/roofing
    python manage.py generate_slots --days=30
    python manage.py generate_slots --reset    # delete all slots first
"""
import random
from datetime import date, time, timedelta

from django.core.management.base import BaseCommand

from booking.models import TimeSlot

SERVICES = ['plumbing', 'electrical', 'roofing']

SLOT_TIMES = [
    time(8, 0), time(9, 0), time(10, 0), time(11, 0),
    time(13, 0), time(14, 0), time(15, 0), time(16, 0),
]


class Command(BaseCommand):
    help = 'Generate TimeSlot records for the next N days (~40% pre-booked)'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=14, help='Number of days to generate')
        parser.add_argument('--reset', action='store_true', help='Delete all existing slots first')

    def handle(self, *args, **options):
        if options['reset']:
            deleted, _ = TimeSlot.objects.all().delete()
            self.stdout.write(f'Deleted {deleted} existing slots.')

        today = date.today()
        created = 0

        for day_offset in range(options['days']):
            slot_date = today + timedelta(days=day_offset)
            if slot_date.weekday() == 6:  # skip Sundays
                continue

            for service in SERVICES:
                for slot_time in SLOT_TIMES:
                    is_available = random.random() > 0.4  # ~60% available
                    _, was_created = TimeSlot.objects.get_or_create(
                        date=slot_date,
                        start_time=slot_time,
                        service_type=service,
                        defaults={'is_available': is_available},
                    )
                    if was_created:
                        created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} new time slots.'))
