from django.urls import path

from .views import BookingSubmitView, SlotsAPIView

urlpatterns = [
    path('slots/', SlotsAPIView.as_view(), name='booking_slots'),
    path('submit/', BookingSubmitView.as_view(), name='booking_submit'),
]
