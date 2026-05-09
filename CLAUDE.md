# CLAUDE.md — Contractor Demo Site

## Project Overview

Demo subdomain for a web agency showcasing interactive features to local contractors (plumbers, electricians, roofers). Built with Django + Jinja2 templates. Each feature lives on its own page under `/demo/`.

**Live URL structure:**
- `/` — existing one-page landing (do not touch)
- `/contact/` — landing page contact form (demo only)
- `/demo/` — demo hub with feature cards
- `/demo/quote/` — Instant Quote Calculator
- `/demo/emergency/` — Emergency 24/7 Request
- `/demo/service-area/` — Service Area Map
- `/demo/portfolio/` — Before/After Slider
- `/demo/booking/` — Online Booking Calendar
- `/blog/` — Blog listing
- `/blog/<slug>/` — Article detail

---

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Django 4.2+ |
| Templates | Jinja2 (via `django-jinja`) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| PDF generation | ReportLab |
| Image handling | Pillow |
| Geocoding | geopy + Nominatim (free, no API key) |
| Maps | Leaflet.js (CDN, no API key) |
| Calendar UI | Cal.com Embed (official inline JS widget) |
| Before/After slider | `img-comparison-slider` (CDN, web component) |
| Styling | Tailwind CSS v3 (standalone CLI, compiled to `static/css/tailwind.css`) |
| HTTP client (JS) | fetch API (native, no axios) |
| Captcha | Cloudflare Turnstile (JS embed) |
| Markdown rendering | `markdown` + `bleach` (Python) |

No npm build step. All JS libs loaded via CDN in `base.html`. **Exception:** Tailwind CSS is compiled via the standalone CLI binary (`tailwindcss.exe`). Run `.\build_tailwind.ps1` after adding new Tailwind classes. The compiled output (`static/css/tailwind.css`) is committed to git.

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
│   ├── demo_urls.py          # all /demo/… routes
│   ├── api_urls.py           # all /api/… routes
│   └── wsgi.py
├── apps/
│   ├── demo/                 # demo hub view
│   ├── landing/              # existing landing page → /
│   ├── quote/                # Feature 1
│   ├── emergency/            # Feature 2
│   ├── service_area/         # Feature 3
│   ├── portfolio/            # Feature 4
│   ├── booking/              # Feature 5
│   ├── blog/                 # Blog (content marketing)
│   └── web_quote/            # AI quote form on landing page
├── static/
│   ├── css/
│   │   ├── demo.css
│   │   └── landing/
│   │       └── styles.css
│   ├── js/
│   │   ├── quote.js
│   │   ├── emergency.js
│   │   ├── service_area.js
│   │   ├── booking.js
│   │   ├── easymde_init.js
│   │   └── landing/
│   │       ├── main.js
│   │       └── web_quote.js
│   └── img/
│       └── before_after/     # before_1.jpg, after_1.jpg, etc.
├── templates/
│   ├── base.html             # CDN scripts, nav, footer
│   ├── demo_hub.html
│   ├── landing/
│   │   └── index.html
│   ├── quote/
│   │   └── index.html
│   ├── emergency/
│   │   └── index.html
│   ├── service_area/
│   │   └── index.html
│   ├── portfolio/
│   │   └── index.html
│   ├── booking/
│   │   └── index.html
│   └── blog/
│       ├── base_blog.html
│       ├── index.html
│       └── detail.html
├── media/                    # uploaded portfolio images
├── requirements.txt
├── .env.example
└── CLAUDE.md                 ← this file
```

---

## Django Apps — Responsibilities

### `demo`
- Single view `DemoHubView`, no models
- Renders `demo_hub.html` with feature card grid

### `landing`
- `LandingView` — renders landing page, passes `CF_TURNSTILE_SITE_KEY` to template
- `ContactView` — POST `/contact/`, returns `{'status': 'ok'}` (demo only, no real integration)
- No models
- Do not modify without explicit instruction

### `quote`
- Model `QuoteRequest` stores submissions (name, phone, email, address, zip_code, problem_description, ai_response, ai_error, ip_address)
- `QuoteAIService` in `ai_service.py` calls OpenRouter → `google/gemini-2.5-flash-lite`
- Photos passed as base64 directly to AI API, never saved to disk
- `QuotePageView` → single-page form (not a wizard)
- `QuoteSubmitView` → POST multipart/form-data → Turnstile validation → AI estimate → JSON response
- `QuotePDFView` → POST JSON with estimate → PDF file (ReportLab)
- Rate limit: 5 requests/hour per IP (Django cache)

### `emergency`
- No database models
- `EmergencyPageView` — renders demo page
- `EmergencySubmitView` — POST API, returns random master name + ETA (pure simulation)
- Hardcoded MASTERS dict for plumbing, electrical, roofing, hvac, other
- Never sends real SMS — this is a UI/UX demo only

### `service_area`
- No database models
- `ServiceAreaPageView` — renders map page
- `ZipCheckView` — POST API, uses geopy to geocode zip, checks distance from CENTER point
- CENTER coordinates are set in `service_area/geo.py` — change per client
- Default radius: 35 miles

### `portfolio`
- Model `BeforeAfterProject` — title, service_type (choices: plumbing, electrical, roofing, hvac), before_image, after_image, description, duration, savings, client_location, order
- Images uploaded to `media/portfolio/before/` and `media/portfolio/after/`
- `PortfolioPageView` — renders page, passes queryset + unique service types to template
- No AJAX — all data server-rendered

### `booking`
- No local models — all booking data is stored on Cal.com's side
- Embed: official Cal.com inline JS embed, one namespace per service type (lazy-initialised)
- `CalComService` in `cal_service.py` — queries Cal.com API v2 for the "Next Available Slots" preview block (cached 15 min)
- `BookingPageView` passes to template: `cal_username`, `cal_slugs`, `services_preview`, `service_choices`
- Active service types: `plumbing_leak`, `faucet_toilet`, `electrical` (3 types)
- Setup: create 3 event types in Cal.com dashboard (slugs from `.env`), set `CAL_API_KEY` and `CAL_USERNAME`
- Page works (embed loads) even without `CAL_API_KEY` — only the preview table will be empty
- "Powered by Cal.com" badge is required and placed prominently on the page

### `blog`
- Models: `Category` (name, slug), `Article` (title, slug, category FK, excerpt, content [markdown], cover_image_url, published_at, is_published)
- `BlogListView` — renders listing filtered by `?category=slug`
- `ArticleDetailView` — renders article, converts markdown to HTML via `markdown` lib (fenced_code, tables, nl2br extensions), sanitized with `bleach`
- URLs: `/blog/` and `/blog/<slug>/`
- Templates: `templates/blog/base_blog.html`, `index.html`, `detail.html`
- Content managed via Django admin

### `web_quote`
- Model `WebQuoteRequest` — name, email, phone, trade, budget_range, timeline_pref, project_description, ai_response, ai_error, ip_address, created_at
- `WebQuoteSubmitView` — POST multipart from landing page → Turnstile validation → `WebQuoteAIService` → JSON response
- `WebQuotePDFView` — POST JSON with estimate → PDF file (ReportLab)
- Rate limit: 5 requests/hour per IP (Django cache)
- No page view — the form lives on the landing page at `/`

---

## API Endpoints

All API views return JSON. All POST endpoints expect `Content-Type: application/json` unless noted.
CSRF token must be included in all POST requests (use `getCookie('csrftoken')` in JS).

| Method | URL | App | Description |
|---|---|---|---|
| POST | `/api/quote/submit/` | quote | multipart with photos + description → AI estimate JSON |
| POST | `/api/quote/pdf/` | quote | JSON with estimate → PDF file |
| POST | `/api/web-quote/submit/` | web_quote | multipart from landing page form → AI estimate JSON |
| POST | `/api/web-quote/pdf/` | web_quote | JSON with estimate → PDF file |
| POST | `/api/emergency/submit/` | emergency | Returns `{master_name, eta_minutes, sms_text}` |
| POST | `/api/service-area/check/` | service_area | Returns `{in_zone, city, lat, lng, eta_range}` |
| POST | `/contact/` | landing | Demo contact form — returns `{status: ok}` |
| — | `/demo/booking/` | booking | Cal.com Embed renders booking UI directly on page (no local API) |

---

## URL Routing

The root `config/urls.py` delegates to three sub-routers:
- `config/demo_urls.py` — all `/demo/…` page routes
- `config/api_urls.py` — all `/api/…` API routes
- `blog.urls` — `/blog/` routes
- `landing.urls` — `/` and `/contact/`

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
- Cloudflare Turnstile token included in submission
- Result rendered in right-hand column; on mobile it scrolls into view
- PDF download via `POST /api/quote/pdf/` → blob download

### Web Quote form (landing page)
- Embedded in the landing page, handled by `static/js/landing/web_quote.js`
- Submits as multipart/form-data to `POST /api/web-quote/submit/`
- Cloudflare Turnstile token included in submission
- Same AI + PDF flow as demo quote, but targeted at landing page visitors

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
- Cal.com Embed: official inline widget via `app.cal.com/embed/embed.js`
- One namespace per service (`Cal("init", "plumbing_leak", ...)`) — lazily initialised on first tab click
- `switchService(key)` hides/shows containers, updates tab styles, triggers lazy `Cal.ns[key]("inline", ...)`
- `CalComService.get_all_services_preview()` fetches slot data from Cal.com API v2 (cached 15 min)

### Blog
- Articles stored in DB, content written in Markdown
- `ArticleDetailView` converts Markdown → HTML server-side, sanitized with `bleach`
- Category filter via `?category=slug` query param on listing page

---

## Environment Variables (`.env`)

```
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# OpenRouter AI (for Quote Calculator and Web Quote)
OPENROUTER_API_KEY=your-key-here

# Cloudflare Turnstile (quote form + web_quote form)
# Leave blank in dev — default test keys always pass
CF_TURNSTILE_SITE_KEY=your-site-key-here
CF_TURNSTILE_SECRET_KEY=your-secret-key-here

# Cal.com (for Booking Calendar)
# Get API key: cal.com → Settings → Developer → API Keys
CAL_API_KEY=cal_live_xxxxxxxxxxxx
CAL_USERNAME=your-cal-username
CAL_SLUG_PLUMBING=plumbing-repair
CAL_SLUG_FAUCET=faucet-toilet
CAL_SLUG_ELECTRICAL=electrical-work

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

# Load portfolio seed data (if using fixtures)
python manage.py loaddata portfolio

# Blog content is managed via Django admin — no fixture needed

# Configure Cal.com (one-time setup before first deploy)
# 1. Create account at cal.com (free plan is sufficient)
# 2. Create 3 event types with slugs: plumbing-repair, faucet-toilet, electrical-work
# 3. Set availability (e.g. Mon–Fri 8:00–17:00)
# 4. Set CAL_API_KEY and CAL_USERNAME in .env

# Run dev server
python manage.py runserver
```

---

## Data & Demo Content

- All prices, ETAs, and master names are **simulated** — no real data
- Booking availability is **real** — fetched live from Cal.com (or empty if `CAL_API_KEY` not set)
- Before/After images stored in `media/portfolio/` via Django ImageField (Pillow required)
- Blog articles written in Markdown, stored in DB, managed via `/admin/`

---

## Constraints & Rules

1. **No real integrations** — no Twilio, no Google Calendar API, no payment processing. This is a UI demo only.
2. **No npm / no build step** — all JS via CDN tags in `base.html`. Keep it simple.
3. **One app per feature** — do not put multiple feature views in the same app.
4. **API views are stateless where possible** — emergency view does not write to DB; quote and web_quote persist for analytics only.
5. **CSRF on all POSTs** — always include `X-CSRFToken` header in fetch calls.
6. **Mobile-first** — all pages must work on 375px viewport.
7. **Turnstile on all user-facing forms** — include `CF_TURNSTILE_SITE_KEY` in context and validate token server-side.

---

## Adding a New Feature

1. Create app: `python manage.py startapp feature_name`, move to `apps/`
2. Add to `INSTALLED_APPS` in `config/settings/base.py`
3. Create `apps/feature_name/urls.py` with app_name set
4. Add page routes to `config/demo_urls.py` under `/demo/feature-name/`
5. Add API routes to `config/api_urls.py` under `/api/feature-name/`
6. Create template at `templates/feature_name/index.html` extending `base.html`
7. Add feature card to `templates/demo_hub.html`
