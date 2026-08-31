import random

# ── Service zone config — change per client deployment ──────────────────────
CENTER = (33.7448168212341, -84.38487732662206)  # Atlanta, GA
CENTER_LAT, CENTER_LNG = CENTER

RADIUS_MILES = 35
RADIUS_METERS = RADIUS_MILES * 1609.34  # used by Leaflet L.circle()

# Simple in-process cache — avoids hammering Nominatim with the same ZIP twice
GEOCODE_CACHE = {}


def check_zip(zip_code: str) -> dict:
    """Geocode a US ZIP code and check if it falls inside the service zone.

    Returns a dict with keys:
        found, in_zone, city, state, lat, lng, distance_miles, eta_range
    On failure: {"found": False, "error": "<message>"}
    """
    if zip_code in GEOCODE_CACHE:
        return GEOCODE_CACHE[zip_code]

    try:
        from geopy.distance import geodesic
        from geopy.geocoders import Nominatim

        geolocator = Nominatim(user_agent='contractor-demo')
        location = geolocator.geocode(
            {'postalcode': zip_code, 'country': 'US'},
            timeout=8,
        )

        if not location:
            return {'found': False, 'error': 'ZIP code not found'}

        lat = location.latitude
        lng = location.longitude
        distance = geodesic(CENTER, (lat, lng)).miles
        in_zone = distance <= RADIUS_MILES

        # Prefer OSM raw address dict for reliable city/state extraction
        raw_addr = getattr(location, 'raw', {}).get('address', {})
        city = (
            raw_addr.get('city')
            or raw_addr.get('town')
            or raw_addr.get('village')
            or raw_addr.get('municipality')
            or location.address.split(',')[0].strip()
        )
        state = raw_addr.get('state', '')

        eta_range = None
        if in_zone:
            eta_min = random.randint(18, 35)
            eta_max = min(eta_min + random.randint(7, 12), 45)
            eta_range = f'{eta_min}\u2013{eta_max} min'

        result = {
            'found': True,
            'in_zone': in_zone,
            'city': city,
            'state': state,
            'lat': lat,
            'lng': lng,
            'distance_miles': round(distance, 1),
            'eta_range': eta_range,
        }

        GEOCODE_CACHE[zip_code] = result
        return result

    except Exception as e:
        if 'timed out' in str(e).lower() or 'timeout' in str(e).lower():
            return {'found': False, 'error': 'Network error — please try again'}
        return {'found': False, 'error': 'Network error — please try again'}
