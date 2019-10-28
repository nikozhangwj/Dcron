from django.views.generic import TemplateView
from django_celery_beat.models import PeriodicTask


class DemoView(TemplateView):
    template_name = 'demo.html'

    def get_context_data(self, **kwargs):
        context = {
            'scheduled_tasks': PeriodicTask.objects.all()
        }
        kwargs.update(context)
        return super(DemoView, self).get_context_data(**kwargs)


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = {
            'scheduled_tasks': PeriodicTask.objects.all()
        }
        kwargs.update(context)
        return super(IndexView, self).get_context_data(**kwargs)
