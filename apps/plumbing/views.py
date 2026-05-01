import io
import re
from datetime import date

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views import View

from quote.ai_service import QuoteAIService
from quote.models import QuoteRequest
from quote.utils import files_to_base64
from quote.views import _check_rate_limit, _verify_turnstile

from .models import PlumbingBusiness
from .translations import TRANSLATIONS


class PlumbingLandingView(View):
    def get(self, request, slug):
        business = get_object_or_404(PlumbingBusiness, slug=slug, is_active=True)
        lang = request.session.get('django_language', 'en')

        if lang == 'es':
            tagline = business.tagline_es or business.tagline_en
            description = business.description_es or business.description_en
        else:
            tagline = business.tagline_en
            description = business.description_en

        t = dict(TRANSLATIONS.get(lang, TRANSLATIONS['en']))
        t['hero_badge'] = t['hero_badge'].format(
            review_count=business.review_count,
            city=business.city,
            state=business.state,
        )

        site_key = settings.CF_TURNSTILE_SITE_KEY
        # Turnstile is only active when a real key is configured.
        # Placeholder values ('your-site-key-here', default test key, empty)
        # should not render the widget so they don't block form submission.
        _PLACEHOLDER_KEYS = {'your-site-key-here', '', '1x00000000000000000000AA'}
        turnstile_active = site_key not in _PLACEHOLDER_KEYS

        return TemplateResponse(request, 'plumbing/index.html', {
            'business': business,
            'lang': lang,
            'tagline': tagline,
            'description': description,
            'CF_TURNSTILE_SITE_KEY': site_key,
            'turnstile_active': turnstile_active,
            't': t,
        })


def set_language_view(request, slug, lang):
    if lang not in ('en', 'es'):
        return HttpResponseBadRequest('Invalid language')
    request.session['django_language'] = lang
    return redirect('plumbing:landing', slug=slug)


class PlumbingQuoteSubmitView(View):
    ALLOWED_SERVICE_TYPES = {'plumbing_leak', 'faucet_toilet', 'water_heater'}

    def post(self, request, business_slug):
        business = get_object_or_404(PlumbingBusiness, slug=business_slug, is_active=True)
        ip = request.META.get('REMOTE_ADDR')

        if not _check_rate_limit(ip):
            return JsonResponse(
                {"success": False, "error": "Too many requests. Please try again in an hour."},
                status=429,
            )

        cf_token = request.POST.get('cf-turnstile-response', '')
        if not _verify_turnstile(cf_token, ip):
            return JsonResponse(
                {"success": False, "error": "Captcha verification failed. Please refresh the page and try again."},
                status=400,
            )

        name     = request.POST.get('name', '').strip()
        phone    = request.POST.get('phone', '').strip()
        email    = request.POST.get('email', '').strip()
        address  = request.POST.get('address', '').strip()
        zip_code = request.POST.get('zip_code', '').strip()
        problem  = request.POST.get('problem_description', '').strip()

        _EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$')
        errors = {}
        if not name:
            errors['name'] = 'Name is required.'
        if not phone:
            errors['phone'] = 'Phone is required.'
        else:
            phone_digits = re.sub(r'\D', '', phone)
            if len(phone_digits) < 10 or len(phone_digits) > 15:
                errors['phone'] = 'Enter a valid phone number (10+ digits).'
        if not email:
            errors['email'] = 'Email is required.'
        elif not _EMAIL_RE.match(email):
            errors['email'] = 'Enter a valid email address.'
        if not address:
            errors['address'] = 'Address is required.'
        if not problem:
            errors['problem_description'] = 'Please describe the problem.'
        elif len(problem) < 20:
            errors['problem_description'] = 'Please describe the problem in more detail (20 characters minimum).'
        if zip_code and not re.fullmatch(r'\d{5}', zip_code):
            errors['zip_code'] = 'ZIP code must be 5 digits.'

        if errors:
            return JsonResponse({"success": False, "errors": errors}, status=400)

        photo_files = request.FILES.getlist('photos')
        images = files_to_base64(photo_files) if photo_files else []

        ai_service = QuoteAIService()
        ai_service.SYSTEM_PROMPT = (
            f"You are providing an estimate on behalf of {business.name}, "
            f"a licensed plumbing company. "
        ) + ai_service.SYSTEM_PROMPT

        full_address = f"{address}, {zip_code}" if zip_code else address
        result = ai_service.get_estimate(
            problem_description=problem,
            address=full_address,
            images_base64=images,
        )

        has_error = "error" in result
        QuoteRequest.objects.create(
            name=name,
            phone=phone,
            email=email,
            address=address,
            zip_code=zip_code,
            problem_description=f"[{business.name}] {problem}",
            ai_response=result if not has_error else None,
            ai_error=result.get("error", ""),
        )

        if has_error:
            return JsonResponse({"success": False, "error": result["error"]})

        return JsonResponse({"success": True, "estimate": result})


class PlumbingQuotePDFView(View):
    def post(self, request, business_slug):
        import json
        business = get_object_or_404(PlumbingBusiness, slug=business_slug, is_active=True)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        estimate = data.get('estimate')
        if not estimate or not isinstance(estimate, dict):
            return JsonResponse({'error': 'Missing estimate data'}, status=400)

        name    = data.get('name', 'Customer')
        address = data.get('address', '')
        problem = data.get('problem_description', '')

        buf = _build_plumbing_pdf(business, name, address, problem, estimate)
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)[:30]
        filename = f"estimate_{safe_name}_{date.today().isoformat()}.pdf"

        response = HttpResponse(buf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


def _build_plumbing_pdf(business, name: str, address: str, problem: str, estimate: dict) -> io.BytesIO:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, Image,
    )

    DARK   = colors.HexColor('#111827')
    ACCENT = colors.HexColor('#1d4ed8')
    GREEN  = colors.HexColor('#15803d')
    GRAY   = colors.HexColor('#6b7280')
    LIGHT  = colors.HexColor('#f1f5f9')

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        topMargin=40,
        bottomMargin=0.6 * inch,
        leftMargin=40,
        rightMargin=inch,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    header_style = ParagraphStyle(
        'Header', parent=styles['Normal'],
        fontSize=18, fontName='Helvetica-Bold', textColor=colors.white,
        spaceAfter=4,
    )
    title_style = ParagraphStyle(
        'FE', parent=styles['Normal'],
        fontSize=12, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#60a5fa'), alignment=2,
    )

    if business.logo and business.logo.name:
        try:
            logo_cell = Image(business.logo.path, width=120, height=60)
        except Exception:
            logo_cell = Paragraph(business.name, header_style)
    else:
        logo_cell = Paragraph(business.name, header_style)

    header_table = Table(
        [[logo_cell, Paragraph(f'{business.name} — Plumbing Estimate', title_style)]],
        colWidths=[3.5 * inch, 3.0 * inch],
    )
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK),
        ('TOPPADDING', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('LEFTPADDING', (0, 0), (0, -1), 14),
        ('RIGHTPADDING', (-1, 0), (-1, -1), 14),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(header_table)

    story.append(Paragraph(
        f"Generated: {date.today().strftime('%B %d, %Y')}",
        ParagraphStyle('Date', parent=styles['Normal'], fontSize=8, textColor=GRAY, spaceAfter=12),
    ))

    def section(title):
        story.append(Spacer(1, 8))
        story.append(Table(
            [[Paragraph(title.upper(), ParagraphStyle(
                'ST', parent=styles['Normal'],
                fontSize=8, fontName='Helvetica-Bold', textColor=ACCENT,
            ))]],
            colWidths=[6.5 * inch],
        ))
        story.append(HRFlowable(width='100%', thickness=1, color=ACCENT, spaceAfter=6))

    def kv(label, value):
        story.append(Table(
            [[
                Paragraph(label, ParagraphStyle('KL', parent=styles['Normal'],
                    fontSize=9, fontName='Helvetica-Bold', textColor=GRAY)),
                Paragraph(str(value) if value else '—', ParagraphStyle('KV', parent=styles['Normal'],
                    fontSize=9, textColor=DARK)),
            ]],
            colWidths=[1.8 * inch, 4.7 * inch],
        ))
        story.append(Spacer(1, 3))

    # ── Client ───────────────────────────────────────────────────────────────
    section('Client Information')
    kv('Name:', name)
    kv('Address:', address)
    kv('Submitted:', date.today().strftime('%B %d, %Y'))

    # ── Problem description ──────────────────────────────────────────────────
    section('Problem Description')
    story.append(Paragraph(problem or '—', ParagraphStyle(
        'PD', parent=styles['Normal'], fontSize=9, textColor=DARK, leading=14,
    )))
    story.append(Spacer(1, 6))

    # ── Service type ─────────────────────────────────────────────────────────
    section('Service Type')
    story.append(Paragraph(
        estimate.get('service_type', '—'),
        ParagraphStyle('SType', parent=styles['Normal'],
            fontSize=11, fontName='Helvetica-Bold', textColor=DARK),
    ))
    story.append(Spacer(1, 6))

    # ── Cost range ───────────────────────────────────────────────────────────
    section('Estimated Cost')
    min_p = estimate.get('min_price', 0)
    max_p = estimate.get('max_price', 0)
    story.append(Paragraph(
        f'${min_p:,} – ${max_p:,}',
        ParagraphStyle('Price', parent=styles['Normal'],
            fontSize=28, fontName='Helvetica-Bold', textColor=GREEN),
    ))
    story.append(Spacer(1, 8))

    # ── Breakdown table ──────────────────────────────────────────────────────
    breakdown = estimate.get('breakdown', [])
    if breakdown and isinstance(breakdown, list):
        section('Price Breakdown')
        tbl_data = [[
            Paragraph('Item', ParagraphStyle('TH', parent=styles['Normal'],
                fontSize=8, fontName='Helvetica-Bold', textColor=GRAY)),
            Paragraph('Estimated Cost', ParagraphStyle('TH2', parent=styles['Normal'],
                fontSize=8, fontName='Helvetica-Bold', textColor=GRAY)),
        ]]
        for i, row in enumerate(breakdown):
            tbl_data.append([
                Paragraph(row.get('item', ''), ParagraphStyle('TI', parent=styles['Normal'],
                    fontSize=8, textColor=DARK)),
                Paragraph(row.get('cost', ''), ParagraphStyle('TC', parent=styles['Normal'],
                    fontSize=8, textColor=DARK)),
            ])

        tbl = Table(tbl_data, colWidths=[4.5 * inch, 2.0 * inch])
        tbl_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ]
        for i in range(1, len(tbl_data)):
            if i % 2 == 0:
                tbl_style.append(('BACKGROUND', (0, i), (-1, i), LIGHT))
        tbl.setStyle(TableStyle(tbl_style))
        story.append(tbl)
        story.append(Spacer(1, 8))

    # ── Notes ────────────────────────────────────────────────────────────────
    urgency_note = estimate.get('urgency_note', '')
    assumptions  = estimate.get('assumptions', '')
    if urgency_note or assumptions:
        section('Notes')
        if urgency_note:
            story.append(Paragraph(
                f'⚡ {urgency_note}',
                ParagraphStyle('Note', parent=styles['Normal'],
                    fontSize=8, textColor=colors.HexColor('#92400e'), leading=13),
            ))
            story.append(Spacer(1, 4))
        if assumptions:
            story.append(Paragraph(
                f'ℹ Our assumptions: {assumptions}',
                ParagraphStyle('Assump', parent=styles['Normal'],
                    fontSize=8, textColor=GRAY, leading=13),
            ))
        story.append(Spacer(1, 6))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e5e7eb'), spaceBefore=8))
    disclaimer = estimate.get('disclaimer', 'Final price after on-site inspection.')
    footer_contact = (
        f"{business.name} | {business.phone} | "
        f"{business.address}, {business.city}, {business.state}"
    )
    story.append(Paragraph(
        f'{disclaimer}  •  {footer_contact}',
        ParagraphStyle('Footer', parent=styles['Normal'],
            fontSize=7, textColor=GRAY, alignment=1),
    ))

    doc.build(story)
    buf.seek(0)
    return buf
