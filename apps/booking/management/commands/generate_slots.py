"""
Management command: generate_slots

Creates TimeSlot records for the next N days, starting from tomorrow.
~35% of slots are randomly pre-marked as unavailable (simulates existing bookings).
Slots are service-agnostic (service_type='').

Usage:
    python manage.py generate_slots            # 14 days
    python manage.py generate_slots --days=30
    python manage.py generate_slots --reset    # delete all slots first
"""
import random
from datetime import date, time, timedelta

from django.core.management.base import BaseCommand

from booking.models import TimeSlot

# 8:00–16:00 with 1-hour step → 9 slots per day
SLOT_TIMES = [time(h, 0) for h in range(8, 17)]


class Command(BaseCommand):
    help = 'Generate TimeSlot records for the next N days (~35% pre-booked)'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=14, help='Number of days to generate')
        parser.add_argument('--reset', action='store_true', help='Delete all existing slots first')

    def handle(self, *args, **options):
        if options['reset']:
            deleted, _ = TimeSlot.objects.all().delete()
            self.stdout.write(f'Deleted {deleted} existing slots.')

        today = date.today()
        created = 0
        days = options['days']

        for day_offset in range(1, days + 1):  # start from tomorrow
            slot_date = today + timedelta(days=day_offset)
            if slot_date.weekday() == 6:  # skip Sundays
                continue

            for slot_time in SLOT_TIMES:
                end_time = time(slot_time.hour + 1, 0)
                is_available = random.random() > 0.35  # ~35% unavailable
                _, was_created = TimeSlot.objects.get_or_create(
                    date=slot_date,
                    start_time=slot_time,
                    defaults={
                        'end_time': end_time,
                        'is_available': is_available,
                        'service_type': '',
                    },
                )
                if was_created:
                    created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} slots for {days} days'))
