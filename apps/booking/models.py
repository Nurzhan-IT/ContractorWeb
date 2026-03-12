from django.db import models


class TimeSlot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    service_type = models.CharField(max_length=100, default='general')
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = [['date', 'start_time', 'service_type']]

    def __str__(self):
        return f"{self.date} {self.start_time} ({self.service_type})"


class Booking(models.Model):
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='booking')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} — {self.slot}"
