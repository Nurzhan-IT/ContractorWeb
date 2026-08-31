from django.conf import settings
from django.views.generic import TemplateView

from .cal_service import CalComService


class BookingPageView(TemplateView):
    template_name = 'booking/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cal_username'] = settings.CAL_USERNAME
        ctx['cal_slugs'] = settings.CAL_SLUGS
        ctx['services_preview'] = CalComService().get_all_services_preview()
        ctx['service_choices'] = [
            {'key': 'plumbing_leak', 'label': 'Plumbing Repair', 'duration': '1 hr'},
            {'key': 'faucet_toilet', 'label': 'Faucet & Toilet', 'duration': '1 hr'},
            {'key': 'electrical', 'label': 'Electrical Work', 'duration': '2 hrs'},
        ]
        return ctx
