from django.urls import path

from .views import QuoteWizardView

app_name = 'quote'

urlpatterns = [
    path('', QuoteWizardView.as_view(), name='index'),
]
