from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView


class LandingView(TemplateView):
    template_name = 'landing/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cf_turnstile_site_key'] = settings.CF_TURNSTILE_SITE_KEY
        return ctx


class ContactView(View):
    def post(self, request):
        # Demo only — no real email/CRM integration
        return JsonResponse({'status': 'ok'})
