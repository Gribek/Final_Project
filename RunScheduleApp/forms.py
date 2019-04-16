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
        cleaned_date = super().clean()
        start_date = cleaned_date.get('start_date')
        end_date = cleaned_date.get('end_date')
        day = cleaned_date.get('day')
        if day < start_date:
            self.add_error('day', 'Data treningu nie może być wcześniejsza niż data rozpoczęcia planu')
        if day > end_date:
            self.add_error('day', 'Data treningu nie może być póżniejsza niż data zakończenia planu')
        distance = cleaned_date.get('training_distance')
        if int(distance) <= 0:
            self.add_error('distance_main', 'Dystans musi być większy od 0')
        return cleaned_date


class LoginForm(forms.Form):
    user = forms.CharField(label='Użytkownik')
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('user')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError('Podane dane są niepoprawne')
        return self.cleaned_data


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Nazwa użytkownika')
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    repeat_password = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput)
    name = forms.CharField(label='Imię')
    surname = forms.CharField(label='Nazwisko')
    email = forms.EmailField(label='Adres e-mail:', widget=forms.EmailInput)

    def clean(self):
        cleaned_data = super().clean()
        field1 = cleaned_data.get('password')
        field2 = cleaned_data.get('repeat_password')
        username = cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            self.add_error('username', 'Ten użytkownik już jest w bazie!')
        if field1 != field2:
            self.add_error('repeat_password', 'Password i repeat password muszą być takie same')

        return cleaned_data


class PasswordChangeForm(forms.Form):
    new_password = forms.CharField(label='Nowe hasło', widget=forms.PasswordInput)
    repeat_password = forms.CharField(label='Powtórz nowe hasło', widget=forms.PasswordInput)

    def clean(self):
        cleaned_date = super().clean()
        field1 = cleaned_date.get('new_password')
        field2 = cleaned_date.get('repeat_password')
        if field1 != field2:
            raise ValidationError('Wpisane hasła muszą być takie same')
        return cleaned_date


class EditUserForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {'email': forms.EmailInput()}
        labels = {
            'first_name': ('Imię:'),
            'last_name': ('Nazwisko:'),
            'email': ('Adres e-mail:'),
        }


class SelectActivePlanFrom(forms.Form):

    def __init__(self, *args, **kwargs):
        self.choices = kwargs.pop('choices')
        super(SelectActivePlanFrom, self).__init__(*args, **kwargs)
        self.fields['active_plan'].choices = self.choices

    active_plan = forms.ChoiceField(choices=[], label='Wybierz plan')
