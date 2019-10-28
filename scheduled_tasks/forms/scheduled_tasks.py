from Dcron.celery import app

from django import forms
from django.utils.translation import ugettext_lazy as _
from django_celery_beat.admin import PeriodicTaskForm, TaskChoiceField
from django_celery_beat.models import PeriodicTask


class ScheduledTasksForm(PeriodicTaskForm):

    task = forms.CharField(
        label=_('Task (custom)'),
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'task name', 'readonly': 'readonly'})
    )

    class Meta:
        """Form metadata."""

        model = PeriodicTask
        fields = [
            'name', 'task', 'regtask', 'enabled', 'description', 'interval', 'crontab', 'solar', 'start_time', 'one_off', 'args', 'kwargs'
        ]

        help_texts = {
            'start_time': 'Please follow example time format. 2019-09-20 15:00:00'
        }

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Scheduled Task Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'placeholder': 'Description'
            }),
            'args': forms.Textarea(attrs={
                'class': 'form-control', 'placeholder': 'Description'
            }),
            'kwargs': forms.Textarea(attrs={
                'class': 'form-control', 'placeholder': 'Description'
            }),
            'interval': forms.Select(attrs={
                'class': 'form-control', 'placeholder': 'Interval'
            }),
            'crontab': forms.Select(attrs={
                'class': 'form-control', 'placeholder': 'crontab'
            }),
            'solar': forms.Select(attrs={
                'class': 'form-control', 'placeholder': 'solar'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control', 'placeholder': 'start_time'
            }),
        }
