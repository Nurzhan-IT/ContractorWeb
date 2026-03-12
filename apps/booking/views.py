import json
from datetime import date, datetime, timedelta
from urllib.parse import urlencode

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from .models import Booking, TimeSlot


def make_gcal_url(booking):
    start = datetime.combine(booking.slot.date, booking.slot.start_time)
    end = datetime.combine(booking.slot.date, booking.slot.end_time)
    params = {
        "action": "TEMPLATE",
        "text": f"Home Service: {booking.service_type.replace('_', ' ').title()}",
        "dates": f"{start.strftime('%Y%m%dT%H%M%S')}/{end.strftime('%Y%m%dT%H%M%S')}",
        "details": f"Booking #{booking.id}. Technician will contact you 30 min before arrival.",
        "location": "Your address (confirm via phone)",
    }
    return "https://calendar.google.com/calendar/render?" + urlencode(params)


class BookingPageView(TemplateView):
    template_name = 'booking/index.html'


class SlotsAPIView(View):
    def get(self, request):
        days = int(request.GET.get('days', 14))
        today = date.today()
        end_date = today + timedelta(days=days)

        slots = TimeSlot.objects.filter(
            date__gte=today,
            date__lte=end_date,
        )

        events = []
        for slot in slots:
            dt_start = datetime.combine(slot.date, slot.start_time)
            dt_end = datetime.combine(slot.date, slot.end_time)
            events.append({
                'id': slot.pk,
                'title': 'Available' if slot.is_available else 'Booked',
                'start': dt_start.isoformat(),
                'end': dt_end.isoformat(),
                'backgroundColor': '#22c55e' if slot.is_available else '#9ca3af',
                'extendedProps': {
                    'is_available': slot.is_available,
                    'service_type': slot.service_type,
                },
            })

        return JsonResponse(events, safe=False)


class BookingSubmitView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        slot_id = data.get('slot_id')
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        service_type = data.get('service_type', '').strip()
        comment = data.get('comment', '')

        # Validate required fields
        if not all([slot_id, name, phone, email]):
            return JsonResponse({'error': 'slot_id, name, phone, and email are required'}, status=400)

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'error': 'Invalid email format'}, status=400)

        with transaction.atomic():
            try:
                slot = TimeSlot.objects.select_for_update().get(pk=slot_id, is_available=True)
            except TimeSlot.DoesNotExist:
                return JsonResponse({'error': 'Slot no longer available'}, status=409)

            booking = Booking.objects.create(
                slot=slot,
                name=name,
                phone=phone,
                email=email,
                service_type=service_type,
                comment=comment,
            )
            slot.is_available = False
            slot.save()

        gcal_url = make_gcal_url(booking)

        return JsonResponse({
            'success': True,
            'booking_id': booking.pk,
            'gcal_url': gcal_url,
            'slot_date': slot.date.isoformat(),
            'slot_time': slot.start_time.strftime('%H:%M'),
            'master_note': 'A technician will contact you 30 min before arrival.',
        })
