from django.contrib import admin

from .models import Booking, TimeSlot


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['date', 'start_time', 'end_time', 'service_type', 'is_available']
    list_filter = ['is_available', 'date']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'service_type', 'status', 'slot', 'created_at']
    list_filter = ['service_type', 'status', 'created_at']
