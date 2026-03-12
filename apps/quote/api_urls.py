from django.urls import path

from .views import QuoteCalculateView, QuotePDFView

urlpatterns = [
    path('calculate/', QuoteCalculateView.as_view(), name='quote_calculate'),
    path('pdf/', QuotePDFView.as_view(), name='quote_pdf'),
]
