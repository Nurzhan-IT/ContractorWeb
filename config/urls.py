from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Demo feature pages: /demo/
    path('demo/', include('config.demo_urls')),
    # API endpoints: /api/
    path('api/', include('config.api_urls')),
    # Blog at /blog/ — part of main marketing site for SEO
    path('blog/', include('blog.urls')),
    # Landing page at root / — must come last (prefix '' matches everything)
    path('', include('landing.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
