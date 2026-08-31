from unittest.mock import patch

from booking.views import BookingPageView
from django.test import RequestFactory, TestCase
from django.urls import reverse

_FAKE_PREVIEW = [
    {'service': 'Plumbing Repair', 'slug': 'plumbing-repair', 'next_available': 'N/A', 'total_slots_week': 0},
    {'service': 'Faucet & Toilet', 'slug': 'faucet-toilet', 'next_available': 'N/A', 'total_slots_week': 0},
    {'service': 'Electrical Work', 'slug': 'electrical-work', 'next_available': 'N/A', 'total_slots_week': 0},
]


class BookingPageTestCase(TestCase):
    """Booking has no local models or API — Cal.com Embed owns the whole flow."""

    def setUp(self):
        self.response = self.client.get(reverse('booking:index'))
        self.html = self.response.content.decode()

    def test_page_returns_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_has_cal_embed_script(self):
        self.assertIn('app.cal.com/embed/embed.js', self.html)

    def test_has_powered_by_cal_badge(self):
        self.assertIn('Scheduling powered by', self.html)


class BookingPageContextTestCase(TestCase):
    """get_context_data tested directly via RequestFactory: django-jinja
    doesn't send the template_rendered signal the Django test client relies
    on for response.context, and get_all_services_preview() is mocked so
    this doesn't depend on CAL_API_KEY or make a real network call.
    """

    def setUp(self):
        patcher = patch(
            'booking.views.CalComService.get_all_services_preview',
            return_value=_FAKE_PREVIEW,
        )
        self.addCleanup(patcher.stop)
        patcher.start()

        request = RequestFactory().get('/demo/booking/')
        view = BookingPageView()
        view.setup(request)
        self.ctx = view.get_context_data()

    def test_has_three_service_choices(self):
        keys = {c['key'] for c in self.ctx['service_choices']}
        self.assertEqual(keys, {'plumbing_leak', 'faucet_toilet', 'electrical'})

    def test_has_services_preview(self):
        self.assertEqual(self.ctx['services_preview'], _FAKE_PREVIEW)
