from django.contrib import admin

from .models import WebQuoteRequest


@admin.register(WebQuoteRequest)
class WebQuoteRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'trade', 'budget_range', 'created_at', 'has_error')
    list_filter = ('trade', 'budget_range')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('ai_response', 'ai_error', 'created_at')

    def has_error(self, obj):
        return bool(obj.ai_error)

    has_error.boolean = True
    has_error.short_description = 'AI Error'
