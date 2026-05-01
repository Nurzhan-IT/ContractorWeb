from django.urls import path, include

from demo.views import DemoHubView

# Demo page URLs mounted at /demo/
#
# URL map:
#   /demo/               → DemoHubView (feature card grid)
#   /demo/quote/         → quote.urls
#   /demo/emergency/     → emergency.urls
#   /demo/service-area/  → service_area.urls
#   /demo/portfolio/     → portfolio.urls
#   /demo/booking/       → booking.urls
#   /demo/plumbing/      → apps.plumbing.urls

urlpatterns = [
    path('', DemoHubView.as_view(), name='demo_hub'),
    path('quote/', include('quote.urls')),
    path('emergency/', include('emergency.urls')),
    path('service-area/', include('service_area.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('booking/', include('booking.urls')),
    path('plumbing/', include('apps.plumbing.urls')),
]
