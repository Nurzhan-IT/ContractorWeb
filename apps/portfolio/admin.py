from django.contrib import admin

from .models import BeforeAfterProject


@admin.register(BeforeAfterProject)
class BeforeAfterProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'service_type', 'created_at']
    list_filter = ['service_type']
