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
from django.views.generic import TemplateView

from .ai_service import QuoteAIService
from .models import QuoteRequest
from .utils import files_to_base64

# ── Turnstile verification ─────────────────────────────────────────────────────

# Keys that should bypass Turnstile verification entirely:
# - Cloudflare's published test secret (always passes, but fails for empty tokens)
# - The .env.example placeholder (Turnstile widget won't render, nothing to verify)
_CF_BYPASS_SECRETS = frozenset(
    {
        '1x0000000000000000000000000000000AA',
        'your-secret-key-here',
    }
)


def _verify_turnstile(token: str, ip: str) -> bool:
    """Verify Cloudflare Turnstile token. Returns True if valid or if key not set."""
    secret = getattr(settings, 'CF_TURNSTILE_SECRET_KEY', '')
    if not secret or secret in _CF_BYPASS_SECRETS:
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
            # Fail open when the secret itself is invalid/placeholder — the token
            # can't be verified without a real secret, so don't block the user.
            if 'invalid-input-secret' in result.get('error-codes', []):
                return True
            return result.get('success', False)
    except Exception:
        return True  # Fail open on network error — rate limit still guards


# ── Rate limiting ─────────────────────────────────────────────────────────────


def _check_rate_limit(ip: str) -> bool:
    """Allow max 5 quote submissions per hour from a single IP."""
    key = f'quote_rl:{ip}'
    count = cache.get(key, 0)
    if count >= 5:
        return False
    cache.set(key, count + 1, timeout=3600)
    return True


# ── Page view ─────────────────────────────────────────────────────────────────


class QuotePageView(TemplateView):
    template_name = 'quote/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cf_turnstile_site_key'] = settings.CF_TURNSTILE_SITE_KEY
        return ctx


# ── API: Submit (multipart + optional photos) ─────────────────────────────────


class QuoteSubmitView(View):
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
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        zip_code = request.POST.get('zip_code', '').strip()
        problem = request.POST.get('problem_description', '').strip()

        # --- Validation ---
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
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # --- Process uploaded photos ---
        photo_files = request.FILES.getlist('photos')
        images = files_to_base64(photo_files) if photo_files else []

        # --- Call AI ---
        service = QuoteAIService()
        full_address = f'{address}, {zip_code}' if zip_code else address
        result = service.get_estimate(
            problem_description=problem,
            address=full_address,
            images_base64=images,
        )

        # --- Save request to DB ---
        has_error = 'error' in result
        QuoteRequest.objects.create(
            name=name,
            phone=phone,
            email=email,
            address=address,
            zip_code=zip_code,
            problem_description=problem,
            ai_response=result if not has_error else None,
            ai_error=result.get('error', ''),
        )

        if has_error:
            return JsonResponse({'success': False, 'error': result['error']})

        return JsonResponse({'success': True, 'estimate': result})


# ── API: PDF generation ───────────────────────────────────────────────────────


class QuotePDFView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        estimate = data.get('estimate')
        if not estimate or not isinstance(estimate, dict):
            return JsonResponse({'error': 'Missing estimate data'}, status=400)

        name = data.get('name', 'Customer')
        address = data.get('address', '')
        problem = data.get('problem_description', '')

        buf = _build_pdf(name, address, problem, estimate)
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)[:30]
        filename = f'estimate_{safe_name}_{date.today().isoformat()}.pdf'

        response = HttpResponse(buf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ── PDF builder ───────────────────────────────────────────────────────────────


def _build_pdf(name: str, address: str, problem: str, estimate: dict) -> io.BytesIO:
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
    ACCENT = colors.HexColor('#1d4ed8')
    GREEN = colors.HexColor('#15803d')
    GRAY = colors.HexColor('#6b7280')
    LIGHT = colors.HexColor('#f1f5f9')
    YELLOW = colors.HexColor('#fef3c7')

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
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=22,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        'Sub',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica',
        textColor=colors.HexColor('#9ca3af'),
    )

    header_table = Table(
        [
            [
                Paragraph('ContractorPro', header_style),
                Paragraph(
                    'FREE ESTIMATE',
                    ParagraphStyle(
                        'FE',
                        parent=styles['Normal'],
                        fontSize=14,
                        fontName='Helvetica-Bold',
                        textColor=colors.HexColor('#60a5fa'),
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
        # Can't use TableStyle background without proper colWidths trick; use HR instead
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
                            str(value) if value else '—',
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
    kv('Address:', address)
    kv('Submitted:', date.today().strftime('%B %d, %Y'))

    # ── Problem description ──────────────────────────────────────────────────
    section('Problem Description')
    story.append(
        Paragraph(
            problem or '—',
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

    # ── Service type ─────────────────────────────────────────────────────────
    section('Service Type')
    story.append(
        Paragraph(
            estimate.get('service_type', '—'),
            ParagraphStyle('SType', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=DARK),
        )
    )
    story.append(Spacer(1, 6))

    # ── Cost range ───────────────────────────────────────────────────────────
    section('Estimated Cost')
    min_p = estimate.get('min_price', 0)
    max_p = estimate.get('max_price', 0)
    story.append(
        Paragraph(
            f'${min_p:,} – ${max_p:,}',
            ParagraphStyle('Price', parent=styles['Normal'], fontSize=28, fontName='Helvetica-Bold', textColor=GREEN),
        )
    )
    story.append(Spacer(1, 8))

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
        for i, row in enumerate(breakdown):
            bg = LIGHT if i % 2 == 0 else colors.white
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

    # ── Notes ────────────────────────────────────────────────────────────────
    urgency_note = estimate.get('urgency_note', '')
    assumptions = estimate.get('assumptions', '')
    if urgency_note or assumptions:
        section('Notes')
        if urgency_note:
            story.append(
                Paragraph(
                    f'⚡ {urgency_note}',
                    ParagraphStyle(
                        'Note', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#92400e'), leading=13
                    ),
                )
            )
            story.append(Spacer(1, 4))
        if assumptions:
            story.append(
                Paragraph(
                    f'ℹ Our assumptions: {assumptions}',
                    ParagraphStyle('Assump', parent=styles['Normal'], fontSize=8, textColor=GRAY, leading=13),
                )
            )
        story.append(Spacer(1, 6))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e5e7eb'), spaceBefore=8))
    disclaimer = estimate.get('disclaimer', 'Final price after on-site inspection.')
    story.append(
        Paragraph(
            f'{disclaimer}  •  ContractorPro · (555) 012-3456 · demo@contractorpro.com',
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, textColor=GRAY, alignment=1),
        )
    )

    doc.build(story)
    buf.seek(0)
    return buf
