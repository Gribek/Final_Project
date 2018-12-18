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

class DailyTrainingForm(ModelForm):
    class Meta:
        TRAINING_TYPES = (
            ('', '-----'),
            ('OWB', 'OWB'),
            ('WB', 'WB'),
            ('KROS', 'KROS'),
        )
        ADDITIONAL_TRAINING = (
            ('', '-----'),
            ('P', 'P'),
            ('M3', 'M3'),
        )
        model = DailyTraining
        exclude = ['accomplished', 'workout_plan']
        widgets = {
            'day': DatePicker(),
            'training_type': forms.Select(choices=TRAINING_TYPES),
            'additional': forms.Select(choices=ADDITIONAL_TRAINING),
            'additional_quantity': forms.TextInput(attrs={'placeholder': 'Np. 6x100'})
        }

        # training_type = forms.ChoiceField(choices=TRAINING_TYPES, widgets=forms.RadioSelect)
