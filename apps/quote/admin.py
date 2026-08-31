from django.contrib import admin

from .models import QuoteRequest


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address', 'created_at', 'has_ai_result']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'address', 'problem_description']
    readonly_fields = ['ai_response', 'ai_error', 'created_at']

    def has_ai_result(self, obj):
        return bool(obj.ai_response)

    has_ai_result.boolean = True
    has_ai_result.short_description = 'AI Result'
