import markdown
import bleach
from django.http import Http404
from django.views.generic import TemplateView

from .models import Article, Category

BLEACH_ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4',
    'h5', 'h6', 'blockquote', 'code', 'pre', 'a', 'hr', 'table', 'thead',
    'tbody', 'tr', 'th', 'td',
]
BLEACH_ALLOWED_ATTRS = {'a': ['href', 'title', 'rel']}


def _render_markdown(text):
    html = markdown.markdown(
        text,
        extensions=['fenced_code', 'tables', 'nl2br'],
    )
    return bleach.clean(html, tags=BLEACH_ALLOWED_TAGS, attributes=BLEACH_ALLOWED_ATTRS, strip=True)


class BlogListView(TemplateView):
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        active_slug = self.request.GET.get('category', '')
        qs = Article.objects.filter(is_published=True).select_related('category')
        if active_slug:
            qs = qs.filter(category__slug=active_slug)

        articles = []
        for a in qs:
            articles.append({
                'title':           a.title,
                'slug':            a.slug,
                'excerpt':         a.excerpt,
                'cover_image_url': a.cover_image_url,
                'published_at':    a.published_at,
                'category_name':   a.category.name if a.category else '',
                'category_slug':   a.category.slug if a.category else '',
            })

        categories = list(Category.objects.filter(articles__is_published=True).distinct())

        ctx['articles']        = articles
        ctx['categories']      = categories
        ctx['active_category'] = active_slug
        return ctx


class ArticleDetailView(TemplateView):
    template_name = 'blog/detail.html'

    def get_context_data(self, slug, **kwargs):
        ctx = super().get_context_data(**kwargs)

        try:
            article = Article.objects.select_related('category').get(slug=slug, is_published=True)
        except Article.DoesNotExist:
            raise Http404

        ctx['article'] = {
            'title':           article.title,
            'slug':            article.slug,
            'excerpt':         article.excerpt,
            'cover_image_url': article.cover_image_url,
            'published_at':    article.published_at,
            'updated_at':      article.updated_at,
            'category':        article.category,
            'category_name':   article.category.name if article.category else '',
            'category_slug':   article.category.slug if article.category else '',
            'content_html':    _render_markdown(article.content),
        }

        related_qs = Article.objects.filter(is_published=True).exclude(id=article.id)
        if article.category:
            related_qs = related_qs.filter(category=article.category)
        ctx['related_articles'] = [
            {
                'title':           a.title,
                'slug':            a.slug,
                'cover_image_url': a.cover_image_url,
            }
            for a in related_qs.order_by('-published_at')[:3]
        ]
        return ctx
