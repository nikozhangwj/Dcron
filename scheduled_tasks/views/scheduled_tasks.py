from django.views.generic import TemplateView, UpdateView, ListView
from django.urls import reverse_lazy
from django_celery_beat.models import PeriodicTask

from scheduled_tasks.forms import ScheduledTasksForm
from scheduled_tasks.utils import action_handler


class ScheduledTasksView(ListView):
    template_name = 'scheduled_tasks/list.html'
    queryset = PeriodicTask.objects.all()
    context_object_name = 'scheduled_tasks'

    def get_context_data(self, **kwargs):
        context = {
            # 'scheduled_tasks': PeriodicTask.objects.all()
            'error': kwargs.get('error', None),
        }
        kwargs.update(context)
        return super(ScheduledTasksView, self).get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        return super(ScheduledTasksView, self).get(request, *args, **kwargs)

    def post(self, request, **kwargs):
        # print(self.request.POST)
        action = self.request.POST.get('action')
        select_list = [int(tid) for tid in self.request.POST.getlist('_select_action')]
        self.object_list = self.get_queryset()
        if not action or not select_list:
            return self.render_to_response(self.get_context_data(error='no args found'))

        # print(action)
        # print(select_list)
        action_handler(action=action, select_list=select_list)
        return self.render_to_response(self.get_context_data())


class ScheduledTasksUpdateView(UpdateView):
    template_name = 'scheduled_tasks/update.html'
    form_class = ScheduledTasksForm
    model = PeriodicTask
    success_url = reverse_lazy('scheduled_tasks:scheduled_tasks')
