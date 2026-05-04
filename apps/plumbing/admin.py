from django.contrib import admin
from .models import PlumbingBusiness


@admin.register(PlumbingBusiness)
class PlumbingBusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'city', 'phone', 'review_score', 'review_count', 'is_active')
    list_filter = ('is_active', 'state')
    search_fields = ('name', 'slug', 'city')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Business Info', {
            'fields': ('name', 'slug', 'phone', 'logo', 'is_active'),
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'zip_code'),
        }),
        ('Credentials', {
            'fields': ('years_in_business', 'license_number'),
        }),
        ('Ratings', {
            'fields': ('review_count', 'review_score'),
        }),
        ('Content (EN)', {
            'fields': ('tagline_en', 'description_en'),
        }),
        ('Content (ES)', {
            'fields': ('tagline_es', 'description_es'),
        }),
        ('Map', {
            'fields': ('google_maps_embed_url',),
        }),
    )
