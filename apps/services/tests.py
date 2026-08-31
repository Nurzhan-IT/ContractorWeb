from django.test import TestCase
from django.urls import reverse


class ServicesURLsTestCase(TestCase):
    """Ensure all 14 service URLs resolve to the expected paths."""

    EXPECTED = {
        'services:hub': '/services/',
        'services:contractor_website_design': '/contractor-website-design/',
        'services:construction_website_design': '/construction-website-design/',
        'services:general_contractor_website_design': '/general-contractor-website-design/',
        'services:hvac_website_design': '/hvac-website-design/',
        'services:roofing_website_design': '/roofing-website-design/',
        'services:electrical_contractor_website_design': '/electrical-contractor-website-design/',
        'services:contractor_seo': '/contractor-seo/',
        'services:general_contractor_seo': '/general-contractor-seo/',
        'services:hvac_seo': '/hvac-seo/',
        'services:roofing_seo': '/roofing-seo/',
        'services:plumbing_seo': '/plumbing-seo/',
        'services:contractor_lead_generation': '/contractor-lead-generation/',
        'services:construction_lead_generation': '/construction-lead-generation/',
    }

    def test_all_service_urls_resolve(self):
        for name, expected_path in self.EXPECTED.items():
            with self.subTest(url_name=name):
                self.assertEqual(reverse(name), expected_path)


class ServicePageRenderTestCase(TestCase):
    """Smoke tests: every service page responds 200 and includes core SEO elements."""

    SERVICE_URLS = [
        'services:hub',
        'services:contractor_website_design',
        'services:construction_website_design',
        'services:general_contractor_website_design',
        'services:hvac_website_design',
        'services:roofing_website_design',
        'services:electrical_contractor_website_design',
        'services:contractor_seo',
        'services:general_contractor_seo',
        'services:hvac_seo',
        'services:roofing_seo',
        'services:plumbing_seo',
        'services:contractor_lead_generation',
        'services:construction_lead_generation',
    ]

    def test_every_service_page_returns_200(self):
        for url_name in self.SERVICE_URLS:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200, msg=f'{url_name} returned {response.status_code}')


class HVACServicePageContentTestCase(TestCase):
    """Deep content checks on the reference page."""

    def setUp(self):
        self.response = self.client.get(reverse('services:hvac_website_design'))
        self.html = self.response.content.decode()

    def test_has_primary_keyword_in_h1(self):
        self.assertIn('HVAC Website Design', self.html)

    def test_has_canonical_url(self):
        self.assertIn('https://contractorwebdev.com/hvac-website-design/', self.html)

    def test_has_service_schema(self):
        self.assertIn('"@type": "Service"', self.html)
        self.assertIn('"serviceType": "HVAC Website Design"', self.html)

    def test_has_faq_schema(self):
        self.assertIn('"@type": "FAQPage"', self.html)

    def test_has_breadcrumb_schema(self):
        self.assertIn('"@type": "BreadcrumbList"', self.html)

    def test_has_pricing(self):
        self.assertIn('1,499', self.html)

    def test_has_related_service_links(self):
        self.assertIn('/hvac-seo/', self.html)
        self.assertIn('/contractor-lead-generation/', self.html)


class SitemapContentsTestCase(TestCase):
    """sitemap.xml must list all 13 service pages, the /services/ hub, and landing/demo URLs."""

    def setUp(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.xml = response.content.decode()

    def test_contains_services_hub(self):
        self.assertIn('<loc>http://testserver/services/</loc>', self.xml)

    def test_contains_all_13_service_pages(self):
        expected_paths = [
            '/contractor-website-design/',
            '/construction-website-design/',
            '/general-contractor-website-design/',
            '/hvac-website-design/',
            '/roofing-website-design/',
            '/electrical-contractor-website-design/',
            '/contractor-seo/',
            '/general-contractor-seo/',
            '/hvac-seo/',
            '/roofing-seo/',
            '/plumbing-seo/',
            '/contractor-lead-generation/',
            '/construction-lead-generation/',
        ]
        for path in expected_paths:
            with self.subTest(path=path):
                self.assertIn(f'<loc>http://testserver{path}</loc>', self.xml)

    def test_contains_landing_root(self):
        self.assertIn('<loc>http://testserver/</loc>', self.xml)

    def test_contains_blog_index(self):
        self.assertIn('<loc>http://testserver/blog/</loc>', self.xml)

    def test_contains_demo_hub(self):
        self.assertIn('<loc>http://testserver/demo/</loc>', self.xml)
