import json

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from .pricing import PRICING_CONFIG, calculate_price


class QuoteWizardView(TemplateView):
    template_name = 'quote/index.html'


class QuoteCalculateView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            service_type = data['service_type']
            unit_count = int(data.get('unit_count', 1))
            urgency = data.get('urgency', 'normal')

            if service_type not in PRICING_CONFIG:
                return JsonResponse({'error': 'Unknown service type'}, status=400)
            if urgency not in ('normal', 'urgent', 'emergency'):
                return JsonResponse({'error': 'Invalid urgency'}, status=400)

            min_price, max_price = calculate_price(service_type, unit_count, urgency)
            config = PRICING_CONFIG[service_type]

            return JsonResponse({
                'min_price': min_price,
                'max_price': max_price,
                'breakdown': {
                    'service_type': service_type,
                    'unit_count': unit_count,
                    'urgency': urgency,
                    'unit_label': config['unit_label'],
                },
            })
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            return JsonResponse({'error': str(e)}, status=400)


class QuotePDFView(View):
    def post(self, request):
        # PDF generation via ReportLab — to be implemented
        return JsonResponse({'error': 'Not implemented yet'}, status=501)
