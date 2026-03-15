from django.db import models


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
    cover_image_url = models.URLField(blank=True, help_text='External URL of the cover image')
    published_at    = models.DateTimeField()
    is_published    = models.BooleanField(default=False)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title
