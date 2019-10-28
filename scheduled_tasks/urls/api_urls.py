from django.urls import path


from scheduled_tasks import api

app_name = 'scheduled_tasks'

urlpatterns = [
    path('action/', api.ScheduledTasksActionAPI.as_view(), name='action'),
]