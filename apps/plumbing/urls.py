from django.urls import path
from .views import PlumbingLandingView, set_language_view

app_name = 'plumbing'

urlpatterns = [
    path('<slug:slug>/', PlumbingLandingView.as_view(), name='landing'),
    path('<slug:slug>/set-lang/<str:lang>/', set_language_view, name='set_lang'),
]
