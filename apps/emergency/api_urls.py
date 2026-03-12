from django.urls import path

from .views import EmergencySubmitView

urlpatterns = [
    path('submit/', EmergencySubmitView.as_view(), name='emergency_submit'),
]
