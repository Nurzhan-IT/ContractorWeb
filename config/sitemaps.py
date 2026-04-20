from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Article


class LandingSitemap(Sitemap):
    priority = 1.0
    changefreq = 'monthly'

    def items(self):
        return ['landing:landing']

    def location(self, item):
        return reverse(item)


class DemoSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return [
            'demo_hub',
            'quote:quote',
            'emergency:index',
            'service_area:index',
            'portfolio:index',
            'booking:index',
        ]

    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.published_at


class BlogIndexSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return ['blog:index']

    def location(self, item):
        return reverse(item)


class ServicePagesSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return [
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

    def location(self, item):
        return reverse(item)
