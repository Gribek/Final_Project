from django.contrib.postgres.forms import RangeWidget
from django import forms
from django.core.exceptions import ValidationError
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


class WorkoutPlanEditForm(ModelForm):
    class Meta:
        model = WorkoutPlan
        exclude = ['owner', 'is_active']
        widgets = {
            'date_range': RangeWidget(DatePicker())
        }


class DailyTrainingForm(ModelForm):
    class Meta:
        TRAINING_TYPES = (  # TODO dopisz rodzaje treningu
            ('', '-----'),
            ('TR', 'TR'),
            ('OWB', 'OWB'),
            ('WB', 'WB'),
            ('WB2', 'WB2'),
            ('WB3', 'WB3'),
            ('KROS pas', 'KROS pas'),
            ('KROS akt', 'KROS akt'),
            ('BNP', 'BNP'),
            ('WT', 'WT'),
        )
        ADDITIONAL_TRAINING = (  # TODO dopisz dodatkowe
            ('', '-----'),
            ('P', 'P'),
            ('M3', 'M3'),
            ('SB', 'SB'),
            # ('GR', 'GR'),
            # ('GS', 'GS'),
        )
        model = DailyTraining
        exclude = ['accomplished', 'workout_plan']
        widgets = {
            'day': DatePicker(),
            'training_type': forms.Select(choices=TRAINING_TYPES),
            'additional': forms.Select(choices=ADDITIONAL_TRAINING),
            'additional_quantity': forms.TextInput(attrs={'placeholder': 'Np. 6x100'})
        }


class LoginForm(forms.Form):
    user = forms.CharField(label="Użytkownik")
    password = forms.CharField(label="Hasło", widget=forms.PasswordInput)


class RegistrationForm(forms.Form):
    username = forms.CharField(label="Nazwa użytkownika")
    password = forms.CharField(label="Hasło", widget=forms.PasswordInput)
    repeat_password = forms.CharField(label="Powtórz hasło", widget=forms.PasswordInput)
    name = forms.CharField(label="Imię")
    surname = forms.CharField(label="Nazwisko")
    email = forms.EmailField(label="Adres e-mail:", widget=forms.EmailInput)

    def clean(self):
        cleaned_data = super().clean()
        field1 = cleaned_data.get('password')
        field2 = cleaned_data.get('repeat_password')
        username = cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            self.add_error("username", "Ten użytkownik już jest w bazie!")
        if field1 != field2:
            self.add_error("repeat_password", "Password i repeat password muszą być takie same")

        return cleaned_data


class PasswordChangeForm(forms.Form):
    new_password = forms.CharField(label="Nowe hasło", widget=forms.PasswordInput)
    repeat_password = forms.CharField(label="Powtórz nowe hasło", widget=forms.PasswordInput)

    def clean(self):
        cleaned_date = super().clean()
        field1 = cleaned_date.get('new_password')
        field2 = cleaned_date.get('repeat_password')
        if field1 != field2:
            raise ValidationError("Wpisane hasła muszą być takie same")
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

    active_plan = forms.ChoiceField(choices=[], label="Wybierz plan")
