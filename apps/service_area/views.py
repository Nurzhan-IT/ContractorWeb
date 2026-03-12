import json
import re

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from .geo import CENTER_LAT, CENTER_LNG, RADIUS_MILES, RADIUS_METERS, check_zip


class ServiceAreaPageView(TemplateView):
    template_name = 'service_area/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['center_lat'] = CENTER_LAT
        ctx['center_lng'] = CENTER_LNG
        ctx['radius_miles'] = RADIUS_MILES
        ctx['radius_meters'] = int(RADIUS_METERS)
        return ctx


class ZipCheckView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        zip_code = data.get('zip', '').strip()
        if not re.match(r'^\d{5}$', zip_code):
            return JsonResponse(
                {'error': 'Please enter a valid 5-digit ZIP code'}, status=400
            )

        result = check_zip(zip_code)

        if not result.get('found'):
            return JsonResponse(result, status=404)

        return JsonResponse(result)
