from django.contrib.postgres.forms import RangeWidget
from django import forms
from RunScheduleApp.models import *
from django.forms import ModelForm, DateInput


class DatePicker(DateInput):
    input_type = 'date'

class WorkoutPlanForm(ModelForm):
    class Meta:
        model = WorkoutPlan
        exclude = ['owner']
        widgets = {
            'date_range': RangeWidget(DatePicker())
        }
