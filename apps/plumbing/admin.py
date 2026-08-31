import csv
import io
from decimal import Decimal, InvalidOperation

from django.contrib import admin, messages
from django.shortcuts import render
from django.urls import path

from .models import PlumbingBusiness


def _parse_bool(value):
    return value.strip().lower() in ('true', '1', 'yes')


def _parse_int(value, default=0):
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return default


def _parse_decimal(value, default=Decimal('5.0')):
    try:
        return Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        return default


REQUIRED_COLUMNS = {'name', 'slug'}


def import_csv(csv_file):
    """Parse CSV and upsert PlumbingBusiness rows. Returns results dict."""
    created = updated = skipped = 0
    errors = []

    try:
        text = csv_file.read().decode('utf-8-sig')
    except UnicodeDecodeError:
        csv_file.seek(0)
        text = csv_file.read().decode('latin-1')

    reader = csv.DictReader(io.StringIO(text))
    cols = set(reader.fieldnames or [])

    missing = REQUIRED_COLUMNS - cols
    if missing:
        return {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': [{'row': 'header', 'msg': f'Missing required columns: {missing}'}],
        }

    for row_num, row in enumerate(reader, start=2):
        slug = row.get('slug', '').strip()
        name = row.get('name', '').strip()

        if not slug or not name:
            errors.append({'row': row_num, 'msg': 'Empty slug or name — skipped'})
            skipped += 1
            continue

        defaults = {
            'name': name,
            'phone': row.get('phone', '').strip(),
            'email': row.get('email', '').strip(),
            'address': row.get('address', '').strip(),
            'city': row.get('city', '').strip(),
            'state': row.get('state', '').strip(),
            'zip_code': row.get('zip_code', '').strip(),
            'review_count': _parse_int(row.get('review_count', '0')),
            'review_score': _parse_decimal(row.get('review_score', '5.0')),
            'years_in_business': _parse_int(row.get('years_in_business', '1'), default=1),
            'license_number': row.get('license_number', '').strip(),
            'tagline_en': row.get('tagline_en', '').strip(),
            'tagline_es': row.get('tagline_es', '').strip(),
            'description_en': row.get('description_en', '').strip(),
            'description_es': row.get('description_es', '').strip(),
            'google_maps_embed_url': row.get('google_maps_embed_url', '').strip(),
            'is_active': _parse_bool(row.get('is_active', 'True')),
        }

        try:
            _, was_created = PlumbingBusiness.objects.update_or_create(slug=slug, defaults=defaults)
            if was_created:
                created += 1
            else:
                updated += 1
        except Exception as exc:
            errors.append({'row': row_num, 'msg': str(exc)})
            skipped += 1

    return {'created': created, 'updated': updated, 'skipped': skipped, 'errors': errors}


@admin.register(PlumbingBusiness)
class PlumbingBusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'city', 'phone', 'review_score', 'review_count', 'is_active')
    list_filter = ('is_active', 'state')
    search_fields = ('name', 'slug', 'city')
    prepopulated_fields = {'slug': ('name',)}
    change_list_template = 'admin/plumbing/plumbingbusiness/change_list.html'
    fieldsets = (
        (
            'Business Info',
            {
                'fields': ('name', 'slug', 'phone', 'logo', 'is_active'),
            },
        ),
        (
            'Location',
            {
                'fields': ('address', 'city', 'state', 'zip_code'),
            },
        ),
        (
            'Credentials',
            {
                'fields': ('years_in_business', 'license_number'),
            },
        ),
        (
            'Ratings',
            {
                'fields': ('review_count', 'review_score'),
            },
        ),
        (
            'Content (EN)',
            {
                'fields': ('tagline_en', 'description_en'),
            },
        ),
        (
            'Content (ES)',
            {
                'fields': ('tagline_es', 'description_es'),
            },
        ),
        (
            'Map',
            {
                'fields': ('google_maps_embed_url',),
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                'import-csv/',
                self.admin_site.admin_view(self.import_csv_view),
                name='plumbing_plumbingbusiness_import_csv',
            ),
        ]
        return custom + urls

    def import_csv_view(self, request):
        results = None

        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                messages.error(request, 'No file uploaded.')
            elif not csv_file.name.endswith('.csv'):
                messages.error(request, 'File must have a .csv extension.')
            else:
                results = import_csv(csv_file)
                if not results['errors'] or results['created'] + results['updated']:
                    msg = (
                        f'Import done: {results["created"]} created, '
                        f'{results["updated"]} updated, {results["skipped"]} skipped.'
                    )
                    messages.success(request, msg)

        context = {
            **self.admin_site.each_context(request),
            'title': 'Import PlumbingBusiness CSV',
            'opts': self.model._meta,
            'results': results,
        }
        return render(request, 'admin/plumbing/plumbingbusiness/import_csv.html', context)
