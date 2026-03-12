from django.urls import path

from .views import QuoteCalculateView, QuotePDFView

urlpatterns = [
    path('calculate/', QuoteCalculateView.as_view()),
    path('pdf/', QuotePDFView.as_view()),
]
