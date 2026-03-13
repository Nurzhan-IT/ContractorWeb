from django.db import models


class QuoteRequest(models.Model):
    # Client info
    name    = models.CharField(max_length=100)
    phone   = models.CharField(max_length=20)
    email   = models.EmailField()
    address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)

    # Problem
    problem_description = models.TextField()

    # AI result (raw JSON)
    ai_response = models.JSONField(null=True, blank=True)
    ai_error    = models.CharField(max_length=500, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Quote #{self.pk} — {self.name} ({self.created_at.date()})"
