from django.urls import path, re_path


from scheduled_tasks import views

app_name = 'scheduled_tasks'

urlpatterns = [
    path('demo/', views.DemoView.as_view(), name='demo'),
    path('index/', views.IndexView.as_view(), name='index'),
    re_path(r'scheduled_tasks/$', views.ScheduledTasksView.as_view(), name='scheduled_tasks'),
    path('scheduled_tasks/update/<pk>', views.ScheduledTasksUpdateView.as_view(), name='scheduled_tasks_update')
]
