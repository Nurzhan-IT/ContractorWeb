from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView


class LandingView(TemplateView):
    template_name = 'landing/index.html'


class ContactView(View):
    def post(self, request):
        # Demo only — no real email/CRM integration
        return JsonResponse({'status': 'ok'})
