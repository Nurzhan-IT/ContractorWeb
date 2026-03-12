from django.views.generic import TemplateView

from .models import BeforeAfterProject


class PortfolioPageView(TemplateView):
    template_name = 'portfolio/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = BeforeAfterProject.objects.all()
        return context
