from django.contrib.auth import authenticate
from django.contrib.postgres.forms import RangeWidget
from django import forms
from django.forms import ModelForm, DateInput
from django.core.exceptions import ValidationError

from RunScheduleApp.models import *


class DatePicker(DateInput):
    input_type = 'date'


class WorkoutPlanForm(ModelForm):
    class Meta:
        model = WorkoutPlan
        exclude = ['owner']
        widgets = {
            'date_range': RangeWidget(DatePicker())
        }


class WorkoutPlanEditForm(ModelForm):
    class Meta:
        model = WorkoutPlan
        exclude = ['owner', 'is_active']
        widgets = {
            'date_range': RangeWidget(DatePicker())
        }


class TrainingForm(ModelForm):
    start_date = forms.DateField(widget=forms.HiddenInput)
    end_date = forms.DateField(widget=forms.HiddenInput)

    class Meta:
        model = Training
        exclude = ['accomplished', 'workout_plan']
        widgets = {
            'day': DatePicker(),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        day = cleaned_data.get('day')
        if day < start_date:
            self.add_error('day', 'The training date cannot be earlier than the workout plan start date')
        if day > end_date:
            self.add_error('day', 'The training date cannot be later than the workout plan end date')
        distance_main = cleaned_data.get('distance_main')
        if distance_main is not None and distance_main <= 0:
            self.add_error('distance_main', 'Distance must be greater than 0')
        distance_additional = cleaned_data.get('distance_additional')
        if distance_additional is not None and distance_additional <= 0:
            self.add_error('distance_additional', 'Distance must be greater than 0')
        time_additional = cleaned_data.get('time_additional')
        if time_additional is not None and time_additional <= 0:
            self.add_error('time_additional', 'Time must be greater than 0')
        return cleaned_data


class LoginForm(forms.Form):
    user = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('user')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError('Invalid username or password')
        return self.cleaned_data


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    repeat_password = forms.CharField(label='Repeat password', widget=forms.PasswordInput)
    name = forms.CharField(label='First name')
    surname = forms.CharField(label='Last name')
    email = forms.EmailField(label='E-mail address:', widget=forms.EmailInput)

    def clean(self):
        cleaned_data = super().clean()
        field1 = cleaned_data.get('password')
        field2 = cleaned_data.get('repeat_password')
        username = cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            self.add_error('username', 'Username already exists')
        if field1 != field2:
            self.add_error('repeat_password', 'Password and Repeat password must be the same')

        return cleaned_data


class PasswordChangeForm(forms.Form):
    new_password = forms.CharField(label='New password', widget=forms.PasswordInput)
    repeat_password = forms.CharField(label='Repeat new password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_date = super().clean()
        field1 = cleaned_date.get('new_password')
        field2 = cleaned_date.get('repeat_password')
        if field1 != field2:
            raise ValidationError('Both passwords must be the same')
        return cleaned_date


class EditUserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {'email': forms.EmailInput()}
        labels = {
            'first_name': 'First name:',
            'last_name': 'Last name:',
            'email': 'E-mail address:',
        }


class SelectActivePlanFrom(forms.Form):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices')
        super(SelectActivePlanFrom, self).__init__(*args, **kwargs)
        self.fields['active_plan'].choices = self.choices

    active_plan = forms.ChoiceField(choices=[], label='Select active workout plan')


class DiaryEntryForm(ModelForm):
    class Meta:
        model = TrainingDiary
        exclude = ['user']
        labels = {
            'date': 'Date of training',
        }
        widgets = {
            'date': RangeWidget(DatePicker())
        }
