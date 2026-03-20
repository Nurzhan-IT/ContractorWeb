from django.db import models


class WebQuoteRequest(models.Model):
    name                = models.CharField(max_length=120)
    email               = models.EmailField()
    phone               = models.CharField(max_length=30, blank=True)
    trade               = models.CharField(max_length=60, blank=True)
    budget_range        = models.CharField(max_length=30, blank=True)
    timeline_pref       = models.CharField(max_length=30, blank=True)
    project_description = models.TextField()
    ai_response         = models.JSONField(null=True, blank=True)
    ai_error            = models.TextField(blank=True, default='')
    created_at          = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.trade} ({self.created_at:%Y-%m-%d})"
