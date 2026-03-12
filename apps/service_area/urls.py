from django.urls import path

from .views import ServiceAreaPageView

app_name = 'service_area'

urlpatterns = [
    path('', ServiceAreaPageView.as_view(), name='index'),
]
