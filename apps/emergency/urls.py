from django.urls import path

from .views import EmergencyPageView

app_name = 'emergency'

urlpatterns = [
    path('', EmergencyPageView.as_view(), name='index'),
]
