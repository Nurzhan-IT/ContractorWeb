import json
from datetime import date, datetime, timedelta

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from .models import Booking, TimeSlot


class BookingPageView(TemplateView):
    template_name = 'booking/index.html'


class SlotsAPIView(View):
    def get(self, request):
        service = request.GET.get('service', 'general')
        days = int(request.GET.get('days', 14))
        today = date.today()
        end_date = today + timedelta(days=days)

        slots = TimeSlot.objects.filter(
            service_type=service,
            date__gte=today,
            date__lte=end_date,
            is_available=True,
        )

        events = []
        for slot in slots:
            dt_start = datetime.combine(slot.date, slot.start_time)
            dt_end = dt_start + timedelta(hours=1)
            events.append({
                'id': slot.pk,
                'title': 'Available',
                'start': dt_start.isoformat(),
                'end': dt_end.isoformat(),
                'extendedProps': {'service_type': slot.service_type},
            })

        return JsonResponse(events, safe=False)


class BookingSubmitView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            slot_id = data['slot_id']
            slot = TimeSlot.objects.get(pk=slot_id, is_available=True)

            booking = Booking.objects.create(
                slot=slot,
                customer_name=data['customer_name'],
                customer_email=data['customer_email'],
                customer_phone=data.get('customer_phone', ''),
                notes=data.get('notes', ''),
            )

            slot.is_available = False
            slot.save()

            # Google Calendar URL — URL scheme only, no OAuth
            dt_start = datetime.combine(slot.date, slot.start_time)
            dt_end = dt_start + timedelta(hours=1)
            gcal_url = (
                "https://calendar.google.com/calendar/render?action=TEMPLATE"
                f"&text={slot.service_type}+Service+Appointment"
                f"&dates={dt_start.strftime('%Y%m%dT%H%M%S')}"
                f"/{dt_end.strftime('%Y%m%dT%H%M%S')}"
                "&details=Booked+via+ContractorPro+Demo"
            )

            return JsonResponse({
                'success': True,
                'booking_id': booking.pk,
                'gcal_url': gcal_url,
            })
        except TimeSlot.DoesNotExist:
            return JsonResponse({'error': 'Slot not available'}, status=409)
        except (json.JSONDecodeError, KeyError) as e:
            return JsonResponse({'error': str(e)}, status=400)
