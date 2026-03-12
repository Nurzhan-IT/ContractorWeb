from django.db import models

SERVICE_DURATIONS = {
    "plumbing_leak": 1.0,
    "faucet_toilet": 1.0,
    "water_heater":  3.0,
    "electrical":    2.0,
    "roofing":       6.0,
}


class TimeSlot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    service_type = models.CharField(max_length=50, blank=True)  # empty = any service
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['date', 'start_time']

    def __str__(self):
        return f"{self.date} {self.start_time}–{self.end_time}"


class Booking(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='booking')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    service_type = models.CharField(max_length=50)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")

    def __str__(self):
        return f"{self.name} — {self.slot}"
