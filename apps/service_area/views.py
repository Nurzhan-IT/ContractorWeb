import json

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from .geo import CENTER_LAT, CENTER_LNG, RADIUS_MILES


class ServiceAreaPageView(TemplateView):
    template_name = 'service_area/index.html'


class ZipCheckView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            zip_code = data.get('zip', '').strip()
            if not zip_code:
                return JsonResponse({'error': 'zip is required'}, status=400)

            # Lazy import — geopy not required at module load time
            from geopy.geocoders import Nominatim
            from geopy.distance import geodesic

            geolocator = Nominatim(user_agent='contractor_demo_v1')
            location = geolocator.geocode({'postalcode': zip_code, 'country': 'US'})
            if not location:
                return JsonResponse({'error': 'ZIP code not found'}, status=404)

            distance = geodesic(
                (CENTER_LAT, CENTER_LNG),
                (location.latitude, location.longitude),
            ).miles
            in_zone = distance <= RADIUS_MILES

            return JsonResponse({
                'in_zone': in_zone,
                'city': location.address.split(',')[0],
                'lat': location.latitude,
                'lng': location.longitude,
                'eta_range': '20-40 min' if in_zone else None,
                'distance_miles': round(distance, 1),
            })
        except (json.JSONDecodeError, KeyError) as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Geocoding failed: ' + str(e)}, status=500)
