# encoding: utf-8
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dcron.settings')

from django.conf import settings

app = Celery('Dcron')

# configs = {k: v for k, v in settings.__dict__.items() if k.startswith('CELERY')}

app.config_from_object(settings, namespace='CELERY')
# app.namespace = 'CELERY'
# app.conf.update(configs)
app.autodiscover_tasks(lambda: [app_config.split('.')[0] for app_config in settings.INSTALLED_APPS])
