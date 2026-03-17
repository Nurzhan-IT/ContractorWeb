from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class LandingSitemap(Sitemap):
    priority = 1.0
    changefreq = 'monthly'

    def items(self):
        return ['landing:index']

    def location(self, item):
        return reverse(item)


class DemoSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return [
            'demo_hub',
            'quote:index',
            'emergency:index',
            'service_area:index',
            'portfolio:index',
            'booking:index',
        ]

    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return ['blog:index']

    def location(self, item):
        return reverse(item)
