from django.contrib import admin

from .models import *
from django_celery_beat.models import PeriodicTask, CrontabSchedule
# Register your models here.

"""
@admin.register(PeriodicTask)
class PeriodicTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'task', 'interval', 'crontab', 'enabled']
    fields = ['name', 'task', 'interval', 'crontab', 'solar', 'args', 'kwargs', 'enabled']


@admin.register(CrontabSchedule)
class CrontabScheduleAdmin(admin.ModelAdmin):
    list_display = ['minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year']
    fields = ['minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year', 'timezone']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'nickname', 'email', 'openid', 'is_active', 'date_joined', 'last_login']
    fields = ['username', 'nickname', 'email', 'openid', 'is_active', 'is_staff', 'groups', 'password']
"""