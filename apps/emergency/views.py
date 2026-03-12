import json
import random

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

# Simulated master names — no real dispatch, UI demo only
_MASTER_NAMES = [
    "Mike Johnson", "Dave Williams", "Tom Anderson", "Chris Davis",
    "Bob Miller", "Steve Wilson", "Jim Moore", "Paul Taylor",
    "Dan Harris", "Mark Thompson",
]


class EmergencyPageView(TemplateView):
    template_name = 'emergency/index.html'


class EmergencySubmitView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            master_name = random.choice(_MASTER_NAMES)
            eta_minutes = random.randint(25, 45)
            service = data.get('service', 'emergency service')
            sms_text = (
                f"Hi! Your request for {service} has been received. "
                f"{master_name} is on the way. ETA: {eta_minutes} minutes. "
                "— ContractorPro Emergency"
            )
            return JsonResponse({
                'master_name': master_name,
                'eta_minutes': eta_minutes,
                'sms_text': sms_text,
            })
        except (json.JSONDecodeError, KeyError) as e:
            return JsonResponse({'error': str(e)}, status=400)
