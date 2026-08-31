from django.urls import path

from . import views

app_name = 'services'

urlpatterns = [
    path('services/', views.ServicesHubView.as_view(), name='hub'),
    path('contractor-website-design/', views.ContractorWebsiteDesignView.as_view(), name='contractor_website_design'),
    path(
        'construction-website-design/',
        views.ConstructionWebsiteDesignView.as_view(),
        name='construction_website_design',
    ),
    path(
        'general-contractor-website-design/',
        views.GeneralContractorWebsiteDesignView.as_view(),
        name='general_contractor_website_design',
    ),
    path('hvac-website-design/', views.HVACWebsiteDesignView.as_view(), name='hvac_website_design'),
    path('roofing-website-design/', views.RoofingWebsiteDesignView.as_view(), name='roofing_website_design'),
    path(
        'electrical-contractor-website-design/',
        views.ElectricalContractorWebsiteDesignView.as_view(),
        name='electrical_contractor_website_design',
    ),
    path('contractor-seo/', views.ContractorSEOView.as_view(), name='contractor_seo'),
    path('general-contractor-seo/', views.GeneralContractorSEOView.as_view(), name='general_contractor_seo'),
    path('hvac-seo/', views.HVACSEOView.as_view(), name='hvac_seo'),
    path('roofing-seo/', views.RoofingSEOView.as_view(), name='roofing_seo'),
    path('plumbing-seo/', views.PlumbingSEOView.as_view(), name='plumbing_seo'),
    path(
        'contractor-lead-generation/', views.ContractorLeadGenerationView.as_view(), name='contractor_lead_generation'
    ),
    path(
        'construction-lead-generation/',
        views.ConstructionLeadGenerationView.as_view(),
        name='construction_lead_generation',
    ),
]
