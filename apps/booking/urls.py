from django.urls import path

from .views import BookingPageView

app_name = 'booking'

urlpatterns = [
    path('', BookingPageView.as_view(), name='index'),
]
