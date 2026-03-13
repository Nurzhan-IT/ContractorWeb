import json
from unittest.mock import patch

from django.test import Client, TestCase, override_settings

from quote.models import QuoteRequest

# Sample AI estimate used in multiple tests
SAMPLE_ESTIMATE = {
    "service_type": "Plumbing — Pipe Repair",
    "min_price": 250,
    "max_price": 450,
    "breakdown": [
        {"item": "Emergency call-out fee", "cost": "$85"},
        {"item": "Pipe repair (labor + materials)", "cost": "$165 – $365"},
    ],
    "urgency_note": "If same-day service is needed, add 40% surcharge.",
    "assumptions": "Standard residential pipe under sink.",
    "disclaimer": "Final price after on-site inspection.",
}

VALID_POST = {
    "name":                "John Smith",
    "phone":               "(555) 000-1234",
    "email":               "john@example.com",
    "address":             "123 Maple St, Atlanta",
    "zip_code":            "30301",
    "problem_description": "My kitchen faucet has been leaking for three days.",
}


class QuoteSubmitWithoutPhotosTest(TestCase):
    """POST /api/quote/submit/ — no photos, mocked AI."""

    def setUp(self):
        self.client = Client()

    @patch('quote.views.QuoteAIService.get_estimate', return_value=SAMPLE_ESTIMATE)
    def test_creates_db_record_and_returns_success(self, mock_ai):
        response = self.client.post(
            '/api/quote/submit/',
            data=VALID_POST,
        )
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertTrue(body['success'])
        self.assertIn('estimate', body)
        self.assertEqual(body['estimate']['min_price'], 250)

        # DB record created
        self.assertEqual(QuoteRequest.objects.count(), 1)
        record = QuoteRequest.objects.first()
        self.assertEqual(record.name, 'John Smith')
        self.assertIsNotNone(record.ai_response)
        self.assertEqual(record.ai_error, '')

    @patch('quote.views.QuoteAIService.get_estimate', return_value={"error": "Connection failed"})
    def test_ai_error_saved_and_returned(self, mock_ai):
        response = self.client.post('/api/quote/submit/', data=VALID_POST)
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertFalse(body['success'])
        self.assertIn('error', body)

        record = QuoteRequest.objects.first()
        self.assertIsNone(record.ai_response)
        self.assertEqual(record.ai_error, 'Connection failed')


class QuoteSubmitValidationTest(TestCase):
    """Input validation for QuoteSubmitView."""

    def setUp(self):
        self.client = Client()

    def test_short_description_returns_400(self):
        data = dict(VALID_POST, problem_description="short")
        response = self.client.post('/api/quote/submit/', data=data)
        self.assertEqual(response.status_code, 400)
        body = json.loads(response.content)
        self.assertFalse(body['success'])
        self.assertIn('problem_description', body.get('errors', {}))

    def test_missing_name_returns_400(self):
        data = dict(VALID_POST, name="")
        response = self.client.post('/api/quote/submit/', data=data)
        self.assertEqual(response.status_code, 400)
        body = json.loads(response.content)
        self.assertIn('name', body.get('errors', {}))

    def test_invalid_zip_returns_400(self):
        data = dict(VALID_POST, zip_code="ABCDE")
        response = self.client.post('/api/quote/submit/', data=data)
        self.assertEqual(response.status_code, 400)
        body = json.loads(response.content)
        self.assertIn('zip_code', body.get('errors', {}))


class QuotePDFTest(TestCase):
    """POST /api/quote/pdf/ — generates a PDF."""

    def setUp(self):
        self.client = Client()

    def test_pdf_generation_returns_pdf(self):
        payload = {
            "estimate": SAMPLE_ESTIMATE,
            "name": "Jane Doe",
            "address": "456 Oak Ave, Atlanta, 30302",
            "problem_description": "Leaking pipe under kitchen sink.",
        }
        response = self.client.post(
            '/api/quote/pdf/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        # PDF magic bytes
        self.assertTrue(response.content[:4] == b'%PDF')

    def test_missing_estimate_returns_400(self):
        response = self.client.post(
            '/api/quote/pdf/',
            data=json.dumps({"name": "Test"}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)


@override_settings(CACHES={
    'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}
})
class QuoteRateLimitTest(TestCase):
    """Rate limit: max 5 requests per hour per IP."""

    @patch('quote.views.QuoteAIService.get_estimate', return_value=SAMPLE_ESTIMATE)
    def test_sixth_request_returns_429(self, mock_ai):
        for _ in range(5):
            r = self.client.post('/api/quote/submit/', data=VALID_POST,
                                 REMOTE_ADDR='10.0.0.1')
            self.assertNotEqual(r.status_code, 429)

        r6 = self.client.post('/api/quote/submit/', data=VALID_POST,
                              REMOTE_ADDR='10.0.0.1')
        self.assertEqual(r6.status_code, 429)
        body = json.loads(r6.content)
        self.assertFalse(body['success'])
        self.assertIn('Too many requests', body['error'])
