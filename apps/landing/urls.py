from django.urls import path

from .views import ContactView, LandingView

app_name = 'landing'

urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
    path('contact/', ContactView.as_view(), name='contact'),
]
