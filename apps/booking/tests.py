import json
from datetime import date, time

from django.test import Client, TestCase

from .models import Booking, TimeSlot


class DoubleBookingTest(TestCase):
    def setUp(self):
        self.slot = TimeSlot.objects.create(
            date=date(2027, 7, 10),
            start_time=time(9, 0),
            end_time=time(10, 0),
            is_available=True,
        )
        self.client = Client()
        self.payload = {
            'slot_id': self.slot.id,
            'name': 'John Doe',
            'phone': '555-1234',
            'email': 'john@example.com',
            'service_type': 'plumbing_leak',
            'comment': '',
        }

    def _post(self):
        return self.client.post(
            '/api/booking/submit/',
            json.dumps(self.payload),
            content_type='application/json',
        )

    def test_first_booking_succeeds(self):
        resp = self._post()
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body['success'])
        self.assertIn('gcal_url', body)
        self.assertIn('booking_id', body)

    def test_double_booking_returns_409(self):
        resp1 = self._post()
        self.assertEqual(resp1.status_code, 200)

        resp2 = self._post()
        self.assertEqual(resp2.status_code, 409)
        self.assertIn('error', resp2.json())

    def test_slot_marked_unavailable_after_booking(self):
        self._post()
        self.slot.refresh_from_db()
        self.assertFalse(self.slot.is_available)

    def test_missing_required_fields_returns_400(self):
        payload = {'slot_id': self.slot.id, 'name': 'Jane'}
        resp = self.client.post(
            '/api/booking/submit/',
            json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)

    def test_invalid_email_returns_400(self):
        payload = {**self.payload, 'email': 'not-an-email'}
        resp = self.client.post(
            '/api/booking/submit/',
            json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)
