from django.urls import path

from .views import QuotePDFView, QuoteSubmitView

urlpatterns = [
    path('submit/', QuoteSubmitView.as_view()),
    path('pdf/',    QuotePDFView.as_view()),
]
