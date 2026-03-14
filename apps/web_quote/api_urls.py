from django.urls import path

from .views import WebQuoteSubmitView, WebQuotePDFView

urlpatterns = [
    path('submit/', WebQuoteSubmitView.as_view()),
    path('pdf/',    WebQuotePDFView.as_view()),
]
