from django.contrib import admin

from .models import BeforeAfterProject


@admin.register(BeforeAfterProject)
class BeforeAfterProjectAdmin(admin.ModelAdmin):
    list_display = ['order', 'title', 'service_type', 'client_location', 'duration', 'savings']
    list_filter = ['service_type']
    ordering = ['order']
