from django.contrib import admin

from .models import Booking, TimeSlot


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['date', 'start_time', 'service_type', 'is_available']
    list_filter = ['service_type', 'is_available', 'date']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'customer_email', 'slot', 'created_at']
    list_filter = ['slot__service_type', 'created_at']
