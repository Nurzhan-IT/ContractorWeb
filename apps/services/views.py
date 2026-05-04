from django.conf import settings
from django.views.generic import TemplateView


class BaseServiceView(TemplateView):
    """Shared context for every service landing page."""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['cf_turnstile_site_key'] = getattr(settings, 'CF_TURNSTILE_SITE_KEY', '')
        ctx['agency_name'] = 'ContractorWebDev'
        ctx['agency_price'] = '2,499'
        return ctx


class ServicesHubView(BaseServiceView):
    template_name = 'services/hub.html'


class ContractorWebsiteDesignView(BaseServiceView):
    template_name = 'services/contractor_website_design.html'


class ConstructionWebsiteDesignView(BaseServiceView):
    template_name = 'services/construction_website_design.html'


class GeneralContractorWebsiteDesignView(BaseServiceView):
    template_name = 'services/general_contractor_website_design.html'


class HVACWebsiteDesignView(BaseServiceView):
    template_name = 'services/hvac_website_design.html'


class RoofingWebsiteDesignView(BaseServiceView):
    template_name = 'services/roofing_website_design.html'


class ElectricalContractorWebsiteDesignView(BaseServiceView):
    template_name = 'services/electrical_contractor_website_design.html'


class ContractorSEOView(BaseServiceView):
    template_name = 'services/contractor_seo.html'


class GeneralContractorSEOView(BaseServiceView):
    template_name = 'services/general_contractor_seo.html'


class HVACSEOView(BaseServiceView):
    template_name = 'services/hvac_seo.html'


class RoofingSEOView(BaseServiceView):
    template_name = 'services/roofing_seo.html'


class PlumbingSEOView(BaseServiceView):
    template_name = 'services/plumbing_seo.html'


class ContractorLeadGenerationView(BaseServiceView):
    template_name = 'services/contractor_lead_generation.html'


class ConstructionLeadGenerationView(BaseServiceView):
    template_name = 'services/construction_lead_generation.html'
