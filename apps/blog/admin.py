from django.contrib import admin

from .models import Article, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display       = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display        = ['title', 'category', 'is_published', 'published_at']
    list_filter         = ['is_published', 'category']
    list_editable       = ['is_published']
    prepopulated_fields = {'slug': ('title',)}
    search_fields       = ['title', 'excerpt']
    date_hierarchy      = 'published_at'

    class Media:
        css = {'all': ['https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css']}
        js  = [
            'https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js',
            '/static/js/easymde_init.js',
        ]
