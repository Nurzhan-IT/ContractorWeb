from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from quote.models import QuoteRequest
from web_quote.models import WebQuoteRequest


class Command(BaseCommand):
    help = 'Deletes QuoteRequest and WebQuoteRequest records older than N days (GDPR Art. 5 compliance)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete records older than this many days (default: 90)',
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff = timezone.now() - timedelta(days=days)

        deleted_q, _ = QuoteRequest.objects.filter(created_at__lt=cutoff).delete()
        deleted_wq, _ = WebQuoteRequest.objects.filter(created_at__lt=cutoff).delete()

        self.stdout.write(self.style.SUCCESS(
            f'Deleted {deleted_q} QuoteRequest(s) and {deleted_wq} WebQuoteRequest(s) '
            f'older than {days} days (cutoff: {cutoff.date()})'
        ))
