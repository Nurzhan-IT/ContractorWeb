from django.urls import path

from .views import ZipCheckView

urlpatterns = [
    path('check/', ZipCheckView.as_view(), name='zip_check'),
]
