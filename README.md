# ContractorPro Demo Site

Interactive demo of contractor website features built with Django + Jinja2. Each feature
lives on its own page under `/demo/` and is fully self-contained.

---

## Quick Start (5 commands)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata portfolio
python manage.py generate_slots --days=14
python manage.py runserver
```

Then open http://127.0.0.1:8000/

> Copy `.env.example` to `.env` and set `SECRET_KEY` before first run.

---

## Demo URLs

| URL | Feature |
|-----|---------|
| `/` | Landing page |
| `/demo/` | Demo hub (all feature cards) |
| `/demo/quote/` | Instant Quote Calculator |
| `/demo/emergency/` | Emergency 24/7 Request |
| `/demo/service-area/` | Service Area Map |
| `/demo/portfolio/` | Before/After Slider Gallery |
| `/demo/booking/` | Online Booking Calendar |
| `/admin/` | Django admin |

---

## How to Change the Service Area Center

Open `apps/service_area/geo.py` and update the `CENTER` tuple (line 4):

```python
CENTER = (33.7490, -84.3880)   # Atlanta, GA  ← change to your city's coords
```

Latitude/longitude for any US city can be found at [latlong.net](https://www.latlong.net/).
The radius is set with `RADIUS_MILES = 35` on the line below — change as needed.

---

## How to Add or Edit Portfolio Projects

**Option A — Edit the fixture file** (recommended for bulk changes):

1. Open `apps/portfolio/fixtures/portfolio.json`
2. Add or modify entries following the existing format
3. Reload: `python manage.py loaddata portfolio`

**Option B — Use Django Admin:**

1. Create a superuser: `python manage.py createsuperuser`
2. Go to http://127.0.0.1:8000/admin/ → Before After Projects
3. Add or edit entries directly in the UI

Image files go in `static/img/before_after/` with the convention:
`before_N.jpg` / `after_N.jpg` (where N matches the `order` field).

---

## How to Reset Booking Slots

```bash
# Add 14 fresh days (keeps existing bookings)
python manage.py generate_slots --days=14

# Wipe all slots and bookings and regenerate
python manage.py generate_slots --days=14 --reset
```

Slots are generated with ~40% randomly pre-booked to simulate realistic availability.

---

## Creating a Superuser (for Admin)

```bash
python manage.py createsuperuser
# Follow prompts: username, email, password
```

Then log in at http://127.0.0.1:8000/admin/

---

## Production Deployment

Set these environment variables (see `.env.example`):

```
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ALLOWED_HOSTS=demo.yourdomain.com
```

Then run:

```bash
pip install psycopg2-binary
python manage.py migrate
python manage.py collectstatic --noinput
```

---

## Tech Stack

| Layer | Choice |
|-------|--------|
| Backend | Django 4.2+ |
| Templates | Jinja2 (django-jinja) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| PDF | ReportLab |
| Geocoding | geopy + Nominatim (no API key) |
| Maps | Leaflet.js (CDN) |
| Calendar | FullCalendar.js (CDN) |
| Before/After | img-comparison-slider (CDN) |
| Styling | Tailwind CSS (CDN) |

No npm / no build step — all JS loaded via CDN.
