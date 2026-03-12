from django.views.generic import TemplateView

from .models import BeforeAfterProject


class PortfolioPageView(TemplateView):
    template_name = 'portfolio/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        projects = []
        for p in BeforeAfterProject.objects.all():
            try:
                before_url = p.before_image.url
            except (ValueError, AttributeError):
                before_url = ''
            try:
                after_url = p.after_image.url
            except (ValueError, AttributeError):
                after_url = ''

            projects.append({
                'id': p.pk,
                'title': p.title,
                'service_type': p.service_type,
                'service_type_display': p.get_service_type_display(),
                'before_image_url': before_url,
                'after_image_url': after_url,
                'description': p.description,
                'duration': p.duration,
                'savings': p.savings,
                'client_location': p.client_location,
            })

        # Unique service types present in DB, in choice-definition order
        type_order = [c[0] for c in BeforeAfterProject.SERVICE_CHOICES]
        present = set(
            BeforeAfterProject.objects.values_list('service_type', flat=True)
        )
        service_types = [t for t in type_order if t in present]

        ctx['projects'] = projects
        ctx['service_types'] = service_types
        return ctx
