import logging
from datetime import datetime, date, timedelta
from celery import current_app
from django.utils.translation import ugettext_lazy as _
from django_celery_beat.models import PeriodicTask, PeriodicTasks
from kombu.utils.json import loads

logger = logging.getLogger('scheduled_tasks')


def action_handler(**kwargs):
    action_map = {
        'delete': delete_scheduled_tasks,
        'enable': enable_scheduled_tasks,
        'disable': disable_scheduled_tasks,
        'run': run_scheduled_tasks
    }
    action = kwargs.get("action")

    func = action_map.get(action)

    return func(kwargs.get("select_list"))


def delete_scheduled_tasks(select_list=None):
    try:
        queryset = PeriodicTask.objects.filter(id__in=select_list)
        queryset.delete()
        return True
    except BaseException as error:
        logger.error(str(error))
        return False


def enable_scheduled_tasks(select_list=None):
    try:
        queryset = PeriodicTask.objects.filter(id__in=select_list)
        queryset.update(enabled=True)
        PeriodicTasks.update_changed()
        return True
    except BaseException as error:
        logger.error(str(error))
        return False


def disable_scheduled_tasks(select_list=None):
    try:
        queryset = PeriodicTask.objects.filter(id__in=select_list)
        queryset.update(enabled=False)
        PeriodicTasks.update_changed()
        return True
    except BaseException as error:
        logger.error(str(error))
        return False


def run_scheduled_tasks(select_list=None):
    queryset = PeriodicTask.objects.filter(id__in=select_list)
    try:
        run_tasks(queryset=queryset)
    except BaseException as error:
        logger.error(str(error))
        return False


def run_tasks(queryset):
    celery_app = current_app
    celery_app.loader.import_default_modules()
    tasks = [(celery_app.tasks.get(task.task),
              loads(task.args),
              loads(task.kwargs))
             for task in queryset]
    task_ids = [task.delay(*args, **kwargs)
                for task, args, kwargs in tasks]
    return len(task_ids)


def last_work_day():
    now = datetime.now()
    month = 0 if now.month == 12 else now.month

    future_mouth_first = date(now.year, month + 1, 1)
    last_day = future_mouth_first - timedelta(days=1)

    if last_day.weekday() < 5:
        last_work_day = last_day
    else:
        last_work_day = last_day - timedelta(days=last_day.weekday() - 4)

    return last_work_day
