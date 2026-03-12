from django.db import models


class BeforeAfterProject(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    before_image = models.ImageField(upload_to='before_after/')
    after_image = models.ImageField(upload_to='before_after/')
    service_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
