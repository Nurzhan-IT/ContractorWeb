from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from config.sitemaps import LandingSitemap, DemoSitemap, BlogSitemap

sitemaps = {
    'landing': LandingSitemap,
    'demo': DemoSitemap,
    'blog': BlogSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    # Demo feature pages: /demo/
    path('demo/', include('config.demo_urls')),
    # API endpoints: /api/
    path('api/', include('config.api_urls')),
    # Blog at /blog/ — part of main marketing site for SEO
    path('blog/', include('blog.urls')),
    # Service landing pages — top-level routes, must come BEFORE landing catch-all
    path('', include('services.urls')),
    # Legal pages
    path('privacy/', TemplateView.as_view(template_name='legal/privacy.html'), name='privacy'),
    path('terms/',   TemplateView.as_view(template_name='legal/terms.html'),   name='terms'),
    path('cookies/', TemplateView.as_view(template_name='legal/cookies.html'), name='cookies'),
    # SEO files
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    # Landing page at root / — must come last (prefix '' matches everything)
    path('', include('landing.urls')),
]

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
