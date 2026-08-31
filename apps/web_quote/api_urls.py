from django.urls import path

from .views import WebQuotePDFView, WebQuoteSubmitView

urlpatterns = [
    path('submit/', WebQuoteSubmitView.as_view()),
    path('pdf/', WebQuotePDFView.as_view()),
]
