from django.urls import path

from .views import QuotePageView

app_name = 'quote'

urlpatterns = [
    path('', QuotePageView.as_view(), name='quote'),
]
