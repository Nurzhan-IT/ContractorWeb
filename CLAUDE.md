# CLAUDE.md — Contractor Demo Site

## Project Overview

Demo subdomain for a web agency showcasing interactive features to local contractors (plumbers, electricians, roofers). Built with Django + Jinja2 templates. Each feature lives on its own page under `/demo/`.

**Live URL structure:**
- `/` — existing one-page landing (moved from root, do not touch)
- `/demo/` — demo hub with feature cards
- `/demo/quote/` — Instant Quote Calculator
- `/demo/emergency/` — Emergency 24/7 Request
- `/demo/service-area/` — Service Area Map
- `/demo/portfolio/` — Before/After Slider
- `/demo/booking/` — Online Booking Calendar

---

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Django 4.2+ |
| Templates | Jinja2 (via `django-jinja`) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| PDF generation | ReportLab |
| Geocoding | geopy + Nominatim (free, no API key) |
| Maps | Leaflet.js (CDN, no API key) |
| Calendar UI | FullCalendar.js (CDN, free tier) |
| Before/After slider | `img-comparison-slider` (CDN, web component) |
| Styling | Tailwind CSS (CDN) |
| HTTP client (JS) | fetch API (native, no axios) |

No npm build step. All JS libs loaded via CDN in `base.html`.

---

## Project Structure

```
contractor_demo/
├── manage.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py          # DEBUG=True, SQLite
│   │   └── production.py     # DEBUG=False, PostgreSQL, env vars
│   ├── urls.py               # root URL conf
│   └── wsgi.py
├── apps/
│   ├── landing/              # existing landing page → /
│   ├── quote/                # Feature 1
│   ├── emergency/            # Feature 2
│   ├── service_area/         # Feature 3
│   ├── portfolio/            # Feature 4
│   └── booking/              # Feature 5
├── static/
│   ├── css/
│   │   └── demo.css
│   ├── js/
│   │   ├── quote.js
│   │   ├── emergency.js
│   │   ├── service_area.js
│   │   └── booking.js
│   └── img/
│       └── before_after/     # before_1.jpg, after_1.jpg, etc.
├── templates/
│   ├── base.html             # CDN scripts, nav, footer
│   ├── demo_hub.html
│   ├── landing/
│   ├── quote/
│   │   └── index.html
│   ├── emergency/
│   │   └── index.html
│   ├── service_area/
│   │   └── index.html
│   ├── portfolio/
│   │   └── index.html
│   └── booking/
│       └── index.html
├── requirements.txt
├── .env.example
└── CLAUDE.md                 ← this file
```

---

## Django Apps — Responsibilities

### `landing`
- Single view, no models
- Returns existing landing page HTML
- Do not modify without explicit instruction

### `quote`
- Model `QuoteRequest` stores submissions (without photos — they are not persisted)
- `QuoteAIService` in `ai_service.py` calls OpenRouter → `google/gemini-2.5-flash-lite`
- Photos passed as base64 directly to AI API, never saved to disk
- `QuotePageView` → single-page form (not a wizard)
- `QuoteSubmitView` → POST multipart/form-data → AI estimate → JSON response
- `QuotePDFView` → POST JSON with estimate → PDF file (ReportLab)
- Rate limit: 5 requests/hour per IP (Django cache)

### `emergency`
- No database models
- `EmergencyPageView` — renders demo page
- `EmergencySubmitView` — POST API, returns random master name + ETA (pure simulation)
- Never sends real SMS — this is a UI/UX demo only

### `service_area`
- No database models
- `ServiceAreaPageView` — renders map page
- `ZipCheckView` — POST API, uses geopy to geocode zip, checks distance from CENTER point
- CENTER coordinates are set in `service_area/geo.py` — change per client
- Default radius: 35 miles

### `portfolio`
- Has one model: `BeforeAfterProject`
- Seed data loaded via `fixtures/portfolio.json` (run `python manage.py loaddata portfolio`)
- `PortfolioPageView` — renders page, passes queryset to template
- No AJAX — all data server-rendered

### `booking`
- Has two models: `TimeSlot` and `Booking`
- `generate_slots` management command creates 14 days of slots with ~40% randomly marked as booked
- `BookingPageView` — renders calendar page
- `SlotsAPIView` — GET, returns available slots as JSON for FullCalendar
- `BookingSubmitView` — POST, creates Booking record, marks slot unavailable, returns Google Calendar URL
- Google Calendar integration = URL scheme only (no OAuth, no API key needed)

---

## API Endpoints

All API views return JSON. All POST endpoints expect `Content-Type: application/json`.
CSRF token must be included in all POST requests (use `getCookie('csrftoken')` in JS).

| Method | URL | App | Description |
|---|---|---|---|
| POST | `/api/quote/submit/` | quote | multipart with photos + description → AI estimate JSON |
| POST | `/api/quote/pdf/` | quote | JSON with estimate → PDF file |
| POST | `/api/emergency/submit/` | emergency | Returns `{master_name, eta_minutes, sms_text}` |
| POST | `/api/service-area/check/` | service_area | Returns `{in_zone, city, lat, lng, eta_range}` |
| GET | `/api/booking/slots/` | booking | Params: `?service=roofing&days=14`. Returns slot list |
| POST | `/api/booking/submit/` | booking | Returns `{success, gcal_url, booking_id}` |

---

## Pricing Logic (`quote/pricing.py`)

Price ranges are calculated as: `base_range + (unit_count × per_unit) × urgency_multiplier`

```python
PRICING_CONFIG = {
    "plumbing_leak":  {"base": (150, 300), "per_unit": 50,  "unit_label": "pipes/points"},
    "faucet_toilet":  {"base": (120, 250), "per_unit": 30,  "unit_label": "fixtures"},
    "water_heater":   {"base": (800, 1400),"per_unit": 0,   "unit_label": None},
    "electrical":     {"base": (200, 500), "per_unit": 75,  "unit_label": "outlets/panels"},
    "roofing":        {"base": (300, 600), "per_unit": 2,   "unit_label": "sq ft"},
}

URGENCY_MULTIPLIERS = {
    "normal":    1.0,
    "urgent":    1.4,
    "emergency": 2.0,
}
```

Final output is always a **range**, never a single number. This is intentional for legal/realistic reasons.

---

## Key Frontend Patterns

### AI Quote form (quote)
- Single-page form with drag-and-drop photo upload (no wizard steps)
- Submits as multipart/form-data to `POST /api/quote/submit/`
- Result rendered in right-hand column; on mobile it scrolls into view
- PDF download via `POST /api/quote/pdf/` → blob download

### SMS simulation (emergency)
- Form submit → `fetch('/api/emergency/submit/')` → show spinner
- `setTimeout(2500)` → hide spinner, show SMS bubble (styled div, not a real notification)
- Countdown timer: `setInterval` decrementing from 15:00

### Map (service_area)
- Leaflet initialised on DOMContentLoaded
- Circle drawn with `L.circle(CENTER, {radius: RADIUS_METERS})`
- On zip submit → `fetch('/api/service-area/check/')` → `map.flyTo([lat, lng], 11)`
- Marker color set based on `in_zone` boolean

### Calendar (booking)
- FullCalendar initialized with `eventSources` pointing to `/api/booking/slots/`
- On event click → show booking modal with pre-filled date/time
- On booking submit → show success screen with `gcal_url` as href

---

## Environment Variables (`.env`)

```
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# OpenRouter AI (for Quote Calculator)
OPENROUTER_API_KEY=your-key-here

# Production only
ALLOWED_HOSTS=demo.yourdomain.com
```

---

## Setup Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Load portfolio seed data
python manage.py loaddata portfolio

# Generate booking slots for next 14 days
python manage.py generate_slots --days=14

# Run dev server
python manage.py runserver
```

---

## Data & Demo Content

- All prices, ETAs, master names, and slot availability are **simulated** — no real data
- Before/After images stored in `static/img/before_after/` — filename convention: `before_N.jpg` / `after_N.jpg`
- Portfolio fixture at `apps/portfolio/fixtures/portfolio.json` — edit to add/change projects
- To reset booking slots: `python manage.py generate_slots --days=14 --reset`

---

## Constraints & Rules

1. **No real integrations** — no Twilio, no Google Calendar API, no payment processing. This is a UI demo only.
2. **No npm / no build step** — all JS via CDN tags in `base.html`. Keep it simple.
3. **Jinja2 only** — do not use Django template tags (`{% %}`) in feature templates. Use Jinja2 syntax (`{{ }}`, `{% %}`). `base.html` uses Jinja2 as well.
4. **One app per feature** — do not put multiple feature views in the same app.
5. **API views are stateless where possible** — quote and emergency views do not write to DB.
6. **CSRF on all POSTs** — always include `X-CSRFToken` header in fetch calls.
7. **Mobile-first** — all pages must work on 375px viewport. Wizard steps must be usable on phone.
8. **Do not modify `landing` app** — it serves the existing client-facing landing page.

---

## Adding a New Feature

1. Create app: `python manage.py startapp feature_name`, move to `apps/`
2. Add to `INSTALLED_APPS` in `config/settings/base.py`
3. Create `apps/feature_name/urls.py` with app_name set
4. Include in `config/urls.py` under `/demo/feature-name/` and `/api/feature-name/`
5. Create template at `templates/feature_name/index.html` extending `base.html`
6. Add feature card to `templates/demo_hub.html`