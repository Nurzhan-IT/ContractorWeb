from django.db import models


class PlumbingBusiness(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL: /demo/plumbing/{slug}")
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=200, blank=True)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50, default='')
    zip_code = models.CharField(max_length=10)
    review_count = models.PositiveIntegerField(default=0)
    review_score = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    years_in_business = models.PositiveIntegerField(default=1)
    license_number = models.CharField(max_length=100, blank=True)
    logo = models.ImageField(upload_to='plumbing/logos/', blank=True, null=True)
    tagline_en = models.CharField(max_length=300, blank=True)
    tagline_es = models.CharField(max_length=300, blank=True)
    description_en = models.TextField(blank=True)
    description_es = models.TextField(blank=True)
    google_maps_embed_url = models.TextField(
        blank=True,
        help_text="Полная ссылка из Google Maps → Share → Embed a map → src=...",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Plumbing Businesses'
