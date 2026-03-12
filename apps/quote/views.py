import io
import json
from datetime import date

from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic import TemplateView

from .pricing import PRICING_CONFIG, URGENCY_MULTIPLIERS, calculate_price


class QuoteWizardView(TemplateView):
    template_name = 'quote/index.html'


class QuoteCalculateView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        service = data.get('service', '')
        if service not in PRICING_CONFIG:
            return JsonResponse(
                {'error': f'Unknown service "{service}". Valid: {list(PRICING_CONFIG)}'},
                status=400,
            )

        urgency = data.get('urgency', 'normal')
        if urgency not in URGENCY_MULTIPLIERS:
            return JsonResponse(
                {'error': f'Invalid urgency "{urgency}". Valid: {list(URGENCY_MULTIPLIERS)}'},
                status=400,
            )

        try:
            unit_count = int(data.get('unit_count', 1))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'unit_count must be an integer'}, status=400)

        result = calculate_price(service, unit_count, urgency)

        return JsonResponse({
            **result,
            'service_display': PRICING_CONFIG[service]['display'],
            'contact': {
                'name':     data.get('name', ''),
                'phone':    data.get('phone', ''),
                'email':    data.get('email', ''),
                'zip_code': data.get('zip_code', ''),
            },
        })


class QuotePDFView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        service = data.get('service', '')
        if service not in PRICING_CONFIG:
            return JsonResponse({'error': f'Unknown service "{service}"'}, status=400)

        urgency = data.get('urgency', 'normal')
        if urgency not in URGENCY_MULTIPLIERS:
            return JsonResponse({'error': f'Invalid urgency "{urgency}"'}, status=400)

        try:
            unit_count = int(data.get('unit_count', 1))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'unit_count must be an integer'}, status=400)

        result = calculate_price(service, unit_count, urgency)
        buf = _build_pdf(data, result)

        response = HttpResponse(buf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="contractorpro-estimate.pdf"'
        return response


def _build_pdf(data: dict, result: dict) -> io.BytesIO:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas as rl_canvas

    DARK   = colors.HexColor('#111827')
    ACCENT = colors.HexColor('#1d4ed8')
    GREEN  = colors.HexColor('#15803d')
    GRAY   = colors.HexColor('#6b7280')
    LIGHT  = colors.HexColor('#f1f5f9')

    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=letter)
    W, H = letter
    M = inch

    c.setFillColor(DARK)
    c.rect(0, H - 1.3 * inch, W, 1.3 * inch, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 20)
    c.drawString(M, H - 0.55 * inch, 'ContractorPro - Estimate')
    c.setFont('Helvetica', 9)
    c.setFillColor(colors.HexColor('#9ca3af'))
    c.drawString(M, H - 0.85 * inch, 'Date: ' + date.today().strftime('%B %d, %Y'))

    y = H - 1.65 * inch

    def section_title(title):
        nonlocal y
        y -= 0.12 * inch
        c.setFillColor(LIGHT)
        c.rect(M - 6, y - 5, W - 2 * M + 12, 20, fill=1, stroke=0)
        c.setFillColor(ACCENT)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(M, y + 3, title.upper())
        y -= 0.35 * inch

    def row(label, value):
        nonlocal y
        c.setFillColor(GRAY)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(M, y, label)
        c.setFillColor(DARK)
        c.setFont('Helvetica', 9)
        c.drawString(M + 2.0 * inch, y, str(value) if value else '-')
        y -= 0.25 * inch

    def hline():
        nonlocal y
        c.setStrokeColor(colors.HexColor('#e5e7eb'))
        c.line(M, y, W - M, y)
        y -= 0.2 * inch

    service_key = data.get('service', '')
    cfg = PRICING_CONFIG.get(service_key, {})

    section_title('Service Details')
    row('Service:', cfg.get('display', service_key))
    row('ZIP Code:', data.get('zip_code') or '-')
    row('Urgency:', data.get('urgency', 'normal').capitalize())
    if cfg.get('unit_label') and data.get('unit_count'):
        row('Scope:', str(data['unit_count']) + ' ' + cfg['unit_label'])

    hline()

    section_title('Contact Information')
    row('Name:',  data.get('name') or '-')
    row('Phone:', data.get('phone') or '-')
    row('Email:', data.get('email') or '-')

    hline()

    section_title('Estimated Cost Range')
    min_p = result['min_price']
    max_p = result['max_price']
    c.setFont('Helvetica-Bold', 30)
    c.setFillColor(GREEN)
    c.drawString(M, y, '$' + format(min_p, ',') + '  -  $' + format(max_p, ','))
    y -= 0.55 * inch

    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(GRAY)
    c.drawString(M, y, 'Breakdown:')
    y -= 0.28 * inch

    bd = result['breakdown']
    row('Base cost:', bd['base'])
    if bd['units']:
        row('Materials:', bd['units'])
    if bd['urgency_surcharge']:
        row('Urgency surcharge:', bd['urgency_surcharge'])

    hline()

    c.setFont('Helvetica-Oblique', 8)
    c.setFillColor(GRAY)
    c.drawString(M, y, 'Final price after on-site inspection. This is an estimate only.')

    c.save()
    buf.seek(0)
    return buf
