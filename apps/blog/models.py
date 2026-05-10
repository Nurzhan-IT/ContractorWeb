from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Article(models.Model):
    title           = models.CharField(max_length=200)
    slug            = models.SlugField(unique=True)
    category        = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles'
    )
    excerpt         = models.TextField(max_length=300, help_text='Short summary shown on listing cards')
    content         = models.TextField(help_text='Full article body in Markdown format')
    cover_image     = models.ImageField(upload_to='blog/', blank=True)
    published_at    = models.DateTimeField()
    is_published    = models.BooleanField(default=False)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})
