from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import DjangoModelPermissions, AllowAny
from django_celery_beat.models import PeriodicTask

from scheduled_tasks.utils import action_handler


class ScheduledTasksActionAPI(APIView):

    permission_classes = (AllowAny,)
    queryset = PeriodicTask.objects.all()
    action_list = ['delete', 'enable', 'disable', 'run']

    def dispatch(self, request, *args, **kwargs):
        return super(ScheduledTasksActionAPI, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return Response(dict(code=200, msg='GET'))

    def post(self, request, *args, **kwargs):
        data = self.request.data
        action = data.get("action", None)
        task_id = data.get("id", None)

        if not action or not task_id:
            return Response(dict(code=404, msg='No action error'))

        if action not in self.action_list:
            return Response(dict(code=404, msg='Action type is not allow.'))

        if action_handler(taskid=task_id, action=action):
            return Response(dict(code=200, msg='POST', data=data))
        else:
            return Response(dict(code=500, msg='error'))

    def put(self, request, *args, **kwargs):
        return Response(dict(code=200, msg='PUT'))

    def delete(self, request, *args, **kwargs):
        return Response(dict(code=200, msg='DELETE'))

