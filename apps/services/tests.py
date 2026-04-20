from django.test import TestCase
from django.urls import reverse


class ServicesURLsTestCase(TestCase):
    """Ensure all 14 service URLs resolve to the expected paths."""

    EXPECTED = {
        'services:hub':                                 '/services/',
        'services:contractor_website_design':           '/contractor-website-design/',
        'services:construction_website_design':         '/construction-website-design/',
        'services:general_contractor_website_design':   '/general-contractor-website-design/',
        'services:hvac_website_design':                 '/hvac-website-design/',
        'services:roofing_website_design':              '/roofing-website-design/',
        'services:electrical_contractor_website_design':'/electrical-contractor-website-design/',
        'services:contractor_seo':                      '/contractor-seo/',
        'services:general_contractor_seo':              '/general-contractor-seo/',
        'services:hvac_seo':                            '/hvac-seo/',
        'services:roofing_seo':                         '/roofing-seo/',
        'services:plumbing_seo':                        '/plumbing-seo/',
        'services:contractor_lead_generation':          '/contractor-lead-generation/',
        'services:construction_lead_generation':        '/construction-lead-generation/',
    }

    def test_all_service_urls_resolve(self):
        for name, expected_path in self.EXPECTED.items():
            with self.subTest(url_name=name):
                self.assertEqual(reverse(name), expected_path)
