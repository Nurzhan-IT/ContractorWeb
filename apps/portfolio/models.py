from django.db import models


class BeforeAfterProject(models.Model):
    SERVICE_CHOICES = [
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('roofing', 'Roofing'),
        ('hvac', 'HVAC'),
    ]

    title = models.CharField(max_length=200)
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    before_image = models.ImageField(upload_to='portfolio/before/')
    after_image = models.ImageField(upload_to='portfolio/after/')
    description = models.TextField()
    duration = models.CharField(max_length=50)
    savings = models.CharField(max_length=50, blank=True)
    client_location = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
