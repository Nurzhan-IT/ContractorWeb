import json
import random

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

MASTERS = {
    'plumbing': [{'name': 'Mike Johnson', 'phone': '555-0142'}],
    'electrical': [{'name': 'Carlos Rivera', 'phone': '555-0187'}],
    'roofing': [{'name': 'Dave Thompson', 'phone': '555-0163'}],
    'hvac': [{'name': 'James Wilson', 'phone': '555-0129'}],
    'other': [{'name': 'Tom Bradley', 'phone': '555-0155'}],
}


class EmergencyPageView(TemplateView):
    template_name = 'emergency/index.html'


class EmergencySubmitView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        name = data.get('name', '').strip()
        problem_type = data.get('problem_type', 'other')

        masters_list = MASTERS.get(problem_type, MASTERS['other'])
        master = random.choice(masters_list)
        master_name = master['name']
        master_phone = master['phone']
        eta_minutes = random.randint(12, 24)

        display_name = name if name else 'there'
        sms_text = (
            f"Hi {display_name}! This is {master_name}. I'm a certified {problem_type} specialist. "
            f'On my way to you now, ETA ~{eta_minutes} min. \U0001f4cd Tracking: [demo link]'
        )

        return JsonResponse(
            {
                'master_name': master_name,
                'master_phone': master_phone,
                'eta_minutes': eta_minutes,
                'sms_text': sms_text,
                'problem_type': problem_type,
            }
        )
