import io
import json
import re
import urllib.parse
import urllib.request
from datetime import date

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.views import View

from .ai_service import WebQuoteAIService
from .models import WebQuoteRequest

# ── Turnstile verification ─────────────────────────────────────────────────────


def _verify_turnstile(token: str, ip: str) -> bool:
    """Verify Cloudflare Turnstile token. Returns True if valid or if key not set."""
    secret = getattr(settings, 'CF_TURNSTILE_SECRET_KEY', '')
    if not secret:
        return True
    data = urllib.parse.urlencode(
        {
            'secret': secret,
            'response': token,
            'remoteip': ip,
        }
    ).encode()
    try:
        req = urllib.request.Request(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data=data,
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read())
            return result.get('success', False)
    except Exception:
        return True  # Fail open on network error — rate limit still guards


# ── Rate limiting ─────────────────────────────────────────────────────────────


def _check_rate_limit(ip: str) -> bool:
    """Allow max 5 web quote submissions per hour from a single IP."""
    key = f'web_quote_rl:{ip}'
    count = cache.get(key, 0)
    if count >= 5:
        return False
    cache.set(key, count + 1, timeout=3600)
    return True


# ── API: Submit (multipart/form-data) ─────────────────────────────────────────


class WebQuoteSubmitView(View):
    def post(self, request):
        ip = request.META.get('REMOTE_ADDR')

        if not _check_rate_limit(ip):
            return JsonResponse(
                {'success': False, 'error': 'Too many requests. Please try again in an hour.'},
                status=429,
            )

        # --- Turnstile ---
        cf_token = request.POST.get('cf-turnstile-response', '')
        if not _verify_turnstile(cf_token, ip):
            return JsonResponse(
                {'success': False, 'error': 'Captcha verification failed. Please refresh the page and try again.'},
                status=400,
            )

        # --- Parse fields from multipart/form-data ---
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        trade = request.POST.get('trade', '').strip()
        budget_range = request.POST.get('budget_range', '').strip()
        timeline_pref = request.POST.get('timeline_pref', '').strip()
        description = request.POST.get('project_description', '').strip()

        # --- Validation ---
        errors = {}
        if not name:
            errors['name'] = 'Name is required.'
        if not email:
            errors['email'] = 'Email is required.'
        if not trade:
            errors['trade'] = 'Please select your trade.'
        if not description:
            errors['project_description'] = 'Please describe your project.'
        elif len(description) < 20:
            errors['project_description'] = 'Please describe your project in more detail (20 characters minimum).'

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # --- Call AI ---
        service = WebQuoteAIService()
        result = service.get_estimate(
            project_description=description,
            trade=trade,
            budget_range=budget_range,
            timeline_pref=timeline_pref,
        )

        # --- Save to DB ---
        has_error = 'error' in result
        WebQuoteRequest.objects.create(
            name=name,
            email=email,
            phone=phone,
            trade=trade,
            budget_range=budget_range,
            timeline_pref=timeline_pref,
            project_description=description,
            ai_response=result if not has_error else None,
            ai_error=result.get('error', ''),
        )

        if has_error:
            return JsonResponse({'success': False, 'error': result['error']})

        return JsonResponse({'success': True, 'estimate': result})


# ── API: PDF generation ───────────────────────────────────────────────────────


class WebQuotePDFView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        estimate = data.get('estimate')
        if not estimate or not isinstance(estimate, dict):
            return JsonResponse({'error': 'Missing estimate data'}, status=400)

        name = data.get('name', 'Client')
        trade = data.get('trade', '')
        description = data.get('project_description', '')

        buf = _build_pdf_web(name, trade, description, estimate)
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)[:30]
        filename = f'web_estimate_{safe_name}_{date.today().isoformat()}.pdf'

        response = HttpResponse(buf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ── PDF builder ───────────────────────────────────────────────────────────────


def _build_pdf_web(name: str, trade: str, description: str, estimate: dict) -> io.BytesIO:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        HRFlowable,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    DARK = colors.HexColor('#111827')
    ACCENT = colors.HexColor('#0891b2')  # cyan-600 to match landing page palette
    GREEN = colors.HexColor('#15803d')
    GRAY = colors.HexColor('#6b7280')
    LIGHT = colors.HexColor('#f1f5f9')

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        topMargin=0.5 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=inch,
        rightMargin=inch,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    header_table = Table(
        [
            [
                Paragraph(
                    'ContractorWebDev',
                    ParagraphStyle(
                        'Header',
                        parent=styles['Normal'],
                        fontSize=22,
                        fontName='Helvetica-Bold',
                        textColor=colors.white,
                        spaceAfter=4,
                    ),
                ),
                Paragraph(
                    'FREE ESTIMATE',
                    ParagraphStyle(
                        'FE',
                        parent=styles['Normal'],
                        fontSize=14,
                        fontName='Helvetica-Bold',
                        textColor=colors.HexColor('#67e8f9'),
                        alignment=2,
                    ),
                ),
            ]
        ],
        colWidths=[3.5 * inch, 3.0 * inch],
    )
    header_table.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, -1), DARK),
                ('TOPPADDING', (0, 0), (-1, -1), 14),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
                ('LEFTPADDING', (0, 0), (0, -1), 14),
                ('RIGHTPADDING', (-1, 0), (-1, -1), 14),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]
        )
    )
    story.append(header_table)

    story.append(
        Paragraph(
            f'Generated: {date.today().strftime("%B %d, %Y")}',
            ParagraphStyle('Date', parent=styles['Normal'], fontSize=8, textColor=GRAY, spaceAfter=12),
        )
    )

    def section(title):
        story.append(Spacer(1, 8))
        story.append(
            Table(
                [
                    [
                        Paragraph(
                            title.upper(),
                            ParagraphStyle(
                                'ST',
                                parent=styles['Normal'],
                                fontSize=8,
                                fontName='Helvetica-Bold',
                                textColor=ACCENT,
                            ),
                        )
                    ]
                ],
                colWidths=[6.5 * inch],
            )
        )
        story.append(HRFlowable(width='100%', thickness=1, color=ACCENT, spaceAfter=6))

    def kv(label, value):
        story.append(
            Table(
                [
                    [
                        Paragraph(
                            label,
                            ParagraphStyle(
                                'KL', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', textColor=GRAY
                            ),
                        ),
                        Paragraph(
                            str(value) if value else '\u2014',
                            ParagraphStyle('KV', parent=styles['Normal'], fontSize=9, textColor=DARK),
                        ),
                    ]
                ],
                colWidths=[1.8 * inch, 4.7 * inch],
            )
        )
        story.append(Spacer(1, 3))

    # ── Client ───────────────────────────────────────────────────────────────
    section('Client Information')
    kv('Name:', name)
    kv('Trade / Industry:', trade)
    kv('Submitted:', date.today().strftime('%B %d, %Y'))

    # ── Project description ──────────────────────────────────────────────────
    section('Project Description')
    story.append(
        Paragraph(
            description or '\u2014',
            ParagraphStyle(
                'PD',
                parent=styles['Normal'],
                fontSize=9,
                textColor=DARK,
                leading=14,
            ),
        )
    )
    story.append(Spacer(1, 6))

    # ── Project type ─────────────────────────────────────────────────────────
    section('Project Type')
    story.append(
        Paragraph(
            estimate.get('project_type', '\u2014'),
            ParagraphStyle('PT', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=DARK),
        )
    )
    story.append(Spacer(1, 4))

    timeline = estimate.get('timeline', '')
    if timeline:
        story.append(
            Paragraph(
                f'Timeline: {timeline}',
                ParagraphStyle('TL', parent=styles['Normal'], fontSize=9, textColor=GRAY),
            )
        )
    story.append(Spacer(1, 6))

    # ── Cost range ───────────────────────────────────────────────────────────
    section('Estimated Cost')
    min_p = estimate.get('min_price', 0)
    max_p = estimate.get('max_price', 0)
    story.append(
        Paragraph(
            f'${min_p:,} \u2013 ${max_p:,}',
            ParagraphStyle('Price', parent=styles['Normal'], fontSize=28, fontName='Helvetica-Bold', textColor=GREEN),
        )
    )
    story.append(Spacer(1, 8))

    # ── Features included ────────────────────────────────────────────────────
    features = estimate.get('features_included', [])
    if features and isinstance(features, list):
        section('Features Included')
        for feat in features:
            story.append(
                Paragraph(
                    f'\u2022 {feat}',
                    ParagraphStyle(
                        'Feat', parent=styles['Normal'], fontSize=8, textColor=DARK, leading=13, leftIndent=10
                    ),
                )
            )
        story.append(Spacer(1, 6))

    # ── Breakdown table ──────────────────────────────────────────────────────
    breakdown = estimate.get('breakdown', [])
    if breakdown and isinstance(breakdown, list):
        section('Price Breakdown')
        tbl_data = [
            [
                Paragraph(
                    'Item',
                    ParagraphStyle(
                        'TH', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', textColor=GRAY
                    ),
                ),
                Paragraph(
                    'Estimated Cost',
                    ParagraphStyle(
                        'TH2', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', textColor=GRAY
                    ),
                ),
            ]
        ]
        for row in breakdown:
            tbl_data.append(
                [
                    Paragraph(
                        row.get('item', ''), ParagraphStyle('TI', parent=styles['Normal'], fontSize=8, textColor=DARK)
                    ),
                    Paragraph(
                        row.get('cost', ''), ParagraphStyle('TC', parent=styles['Normal'], fontSize=8, textColor=DARK)
                    ),
                ]
            )

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

    # ── Assumptions ──────────────────────────────────────────────────────────
    assumptions = estimate.get('assumptions', '')
    if assumptions:
        section('Notes & Assumptions')
        story.append(
            Paragraph(
                f'\u2139 {assumptions}',
                ParagraphStyle('Assump', parent=styles['Normal'], fontSize=8, textColor=GRAY, leading=13),
            )
        )
        story.append(Spacer(1, 6))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e5e7eb'), spaceBefore=8))
    disclaimer = estimate.get('disclaimer', 'Final price confirmed after discovery call. Prices in USD.')
    story.append(
        Paragraph(
            f'{disclaimer}  \u2022  ContractorWebDev \u00b7 (555) 123-4567 \u00b7 hello@contractorwebdev.com',
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, textColor=GRAY, alignment=1),
        )
    )

    doc.build(story)
    buf.seek(0)
    return buf
