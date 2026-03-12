import json

from django.test import Client, TestCase

from quote.pricing import calculate_price


class QuotePricingTests(TestCase):
    def test_roofing_normal_price_range(self):
        """roofing 500 sq ft normal: base(300-600) + 500*2=1000 => 1300-1600"""
        result = calculate_price('roofing', 500, 'normal')
        self.assertEqual(result['min_price'], 1300)
        self.assertEqual(result['max_price'], 1600)

    def test_emergency_multiplier(self):
        """emergency x2.0: roofing 500 sq ft => 2600-3200"""
        result = calculate_price('roofing', 500, 'emergency')
        self.assertEqual(result['min_price'], 2600)
        self.assertEqual(result['max_price'], 3200)
        self.assertIsNotNone(result['breakdown']['urgency_surcharge'])
        self.assertIn('100%', result['breakdown']['urgency_surcharge'])


class QuoteCalculateAPITests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_invalid_service_returns_400(self):
        response = self.client.post(
            '/api/quote/calculate/',
            data=json.dumps({'service': 'flying_cars', 'unit_count': 1, 'urgency': 'normal'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        body = json.loads(response.content)
        self.assertIn('error', body)
