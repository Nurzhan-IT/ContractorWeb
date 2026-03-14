from django.urls import path, include

# API endpoint URLs mounted at /api/
# All views return JSON. All POST endpoints expect Content-Type: application/json.
# All POST requests must include the X-CSRFToken header.
#
# Endpoint map:
#   POST /api/quote/calculate/      → QuoteCalculateView
#   POST /api/quote/pdf/            → QuotePDFView
#   POST /api/emergency/submit/     → EmergencySubmitView
#   POST /api/service-area/check/   → ZipCheckView
#   (booking has no API endpoints — handled by Cal.com Embed)

urlpatterns = [
    path('quote/', include('quote.api_urls')),
    path('web-quote/', include('web_quote.api_urls')),
    path('emergency/', include('emergency.api_urls')),
    path('service-area/', include('service_area.api_urls')),
]
