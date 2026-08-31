"""
Cal.com API v2 service for fetching available slots preview.

Only used for the informational "Next Available Slots" block on the booking page.
The actual booking UI is handled entirely by the Cal.com Embed.

API docs: https://cal.com/docs/api-reference/v2
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta

from django.conf import settings
from django.core.cache import cache

# Human-readable labels for each service key
_SERVICE_LABELS = {
    'plumbing_leak': 'Plumbing Repair',
    'faucet_toilet': 'Faucet & Toilet',
    'electrical': 'Electrical Work',
}


class CalComService:
    BASE_URL = 'https://api.cal.com/v2'

    def __init__(self):
        self.api_key = settings.CAL_API_KEY
        self.username = settings.CAL_USERNAME

    def _get(self, path: str, params: dict, api_version: str) -> dict:
        """
        GET request to Cal.com API v2.
        Returns parsed JSON dict, or {"status": "error", "error": "..."} on failure.
        """
        try:
            url = f'{self.BASE_URL}{path}?{urllib.parse.urlencode(params)}'
            req = urllib.request.Request(url)
            req.add_header('Authorization', f'Bearer {self.api_key}')
            req.add_header('cal-api-version', api_version)
            with urllib.request.urlopen(req, timeout=8) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.URLError as exc:
            return {'status': 'error', 'error': str(exc)}
        except json.JSONDecodeError as exc:
            return {'status': 'error', 'error': f'JSON decode error: {exc}'}

    def get_upcoming_slots(self, event_slug: str, days: int = 7) -> dict:
        """
        Fetch available slots for the next N days from Cal.com API v2.

        Endpoint: GET /v2/slots
        cal-api-version: 2024-09-04

        Returns:
            {
                "status": "success",
                "slots_by_date": {"2025-07-10": ["09:00", "10:00"], ...},
                "total_available": 5
            }
        If CAL_API_KEY is empty returns {"status": "no_key", "slots_by_date": {}, "total_available": 0}.
        """
        if not self.api_key:
            return {'status': 'no_key', 'slots_by_date': {}, 'total_available': 0}

        today = date.today()
        end_date = today + timedelta(days=days)

        params = {
            'eventTypeSlug': event_slug,
            'username': self.username,
            'start': today.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'timeZone': 'America/New_York',
        }

        data = self._get('/slots', params, '2024-09-04')

        if data.get('status') == 'error':
            return {'status': 'error', 'slots_by_date': {}, 'total_available': 0}

        # Cal.com v2 response shape: {"status": "success", "data": {"slots": {"YYYY-MM-DD": [{"time": "..."}]}}}
        raw_slots = data.get('data', {}).get('slots', {})
        slots_by_date = {}
        total = 0

        for date_str, time_slots in raw_slots.items():
            times = []
            for slot in time_slots:
                # time field: "2025-07-10T09:00:00.000Z"  — take HH:MM portion directly
                raw_time = slot.get('time', '')
                if len(raw_time) >= 16:
                    times.append(raw_time[11:16])
            if times:
                slots_by_date[date_str] = times
                total += len(times)

        return {
            'status': 'success',
            'slots_by_date': slots_by_date,
            'total_available': total,
        }

    def get_all_services_preview(self) -> list:
        """
        Return a preview list (one entry per service) showing next available slot
        and total weekly availability. Cached for 15 minutes.

        Returns:
            [
                {
                    "service": "Plumbing Repair",
                    "slug": "plumbing-repair",
                    "next_available": "Tomorrow at 09:00",
                    "total_slots_week": 12,
                },
                ...
            ]
        """
        cache_key = 'cal_services_preview'
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        today = date.today()
        tomorrow = today + timedelta(days=1)
        result = []

        for service_key, slug in settings.CAL_SLUGS.items():
            label = _SERVICE_LABELS.get(service_key, service_key)

            if not self.api_key:
                result.append(
                    {
                        'service': label,
                        'slug': slug,
                        'next_available': 'N/A',
                        'total_slots_week': 0,
                    }
                )
                continue

            slots_data = self.get_upcoming_slots(slug, days=7)
            slots_by_date = slots_data.get('slots_by_date', {})
            total = slots_data.get('total_available', 0)

            next_available = 'No slots available'
            for date_str in sorted(slots_by_date.keys()):
                times = slots_by_date[date_str]
                if not times:
                    continue
                try:
                    slot_date = date.fromisoformat(date_str)
                    first_time = times[0]
                    if slot_date == today:
                        next_available = f'Today at {first_time}'
                    elif slot_date == tomorrow:
                        next_available = f'Tomorrow at {first_time}'
                    else:
                        days_diff = (slot_date - today).days
                        next_available = f'In {days_diff} days'
                except ValueError:
                    pass
                break

            result.append(
                {
                    'service': label,
                    'slug': slug,
                    'next_available': next_available,
                    'total_slots_week': total,
                }
            )

        cache.set(cache_key, result, 15 * 60)
        return result
