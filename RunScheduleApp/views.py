from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.views import View
from datetime import datetime
from calendar import HTMLCalendar

from RunScheduleApp.forms import *


# Create your views here.
class MainPageView(View):
    def get(self, request):
        return render(request, "RunScheduleApp/main_page.html")


# oblicza counter dla url-a prowadzącego do current_workout_plan
def get_month_counter(plan_start_date):
    day_now = datetime.today().date()
    month_counter = (day_now.year - plan_start_date.year) * 12 + day_now.month - plan_start_date.month
    return month_counter


def get_max_month_counter(plan_start_date, plan_end_date):
    day_now = datetime.today().date()
    month_max_counter = (plan_end_date.year - day_now.year) * 12 + plan_end_date.month - day_now.month
    month_max_counter += get_month_counter(plan_start_date)
    return month_max_counter


def get_user(request):
    current_user = request.user
    return current_user


class WorkoutPlanAdd(View):
    def get(self, request):
        form = WorkoutPlanForm()
        return render(request, 'RunScheduleApp/workout_plan_add.html', {'form': form})

    def post(self, request):
        new_workout_plan = WorkoutPlan()
        form = WorkoutPlanForm(request.POST, instance=new_workout_plan)
        if form.is_valid():
            form.instance.owner = get_user(request)
            # if form.instance.is_active == True:
            #     pass TODO(napisać funkcję deaktywującą inne plany)
            form.save()
            return redirect('/workout_list')
        return render(request, 'RunScheduleApp/workout_plan_add.html', {'form': form})


class WorkoutPlanEdit(View):
    def get(self, request, plan_id):
        workout_plan = WorkoutPlan.objects.get(pk=plan_id)
        if workout_plan.owner != get_user(request):
            raise PermissionDenied
        form = WorkoutPlanEditForm(instance=workout_plan)
        return render(request, 'RunScheduleApp/workout_plan_edit.html', {'form': form})

    def post(self, request, plan_id):
        workout_plan = WorkoutPlan.objects.get(pk=plan_id)
        form = WorkoutPlanEditForm(request.POST, instance=workout_plan)
        if form.is_valid():
            form.save()
            return redirect(f'/plan_details/{plan_id}')
        return render(request, 'RunScheduleApp/workout_plan_edit.html', {'form': form, 'plan_id': plan_id})


class PlanDetailsView(View):
    def get(self, request, id):
        workout_plan = WorkoutPlan.objects.get(pk=id)
        if workout_plan.owner != get_user(request):
            raise PermissionDenied
        month_counter = get_month_counter(workout_plan.date_range.lower)
        return render(request, "RunScheduleApp/plan_details.html",
                      {'workout_plan': workout_plan, 'month_counter': month_counter})


class WorkoutsList(View):
    def get(self, request):
        workout_plans = WorkoutPlan.objects.filter(owner=get_user(request))
        return render(request, "RunScheduleApp/workoutplan_list.html", {'workout_plans': workout_plans})


class DailyTrainingAdd(View):
    def get(self, request, id):
        workout_plan = WorkoutPlan.objects.get(pk=id)
        if workout_plan.owner != get_user(request):
            return HttpResponse('Nie możesz dodać treningu do nie swojego planu!')
        form = DailyTrainingForm()
        return render(request, "RunScheduleApp/daily_training_add.html", {'form': form, 'workout_plan': workout_plan})

    def post(self, request, id):
        new_training = DailyTraining()
        form = DailyTrainingForm(request.POST, instance=new_training)
        if form.is_valid():
            workout = WorkoutPlan.objects.get(pk=id)
            form.instance.workout_plan = workout
            form.save()
            return redirect(f'/plan_details/{id}')
        # return HttpResponse('Not valid')
        return render(request, "RunScheduleApp/daily_training_add.html", {'form': form})


class DailyTrainingEdit(View):
    def get(self, request, plan_id, id):
        workout_plan = WorkoutPlan.objects.get(pk=plan_id)
        if workout_plan.owner != get_user(request):
            raise PermissionDenied
        daily_training = DailyTraining.objects.get(pk=id)
        form = DailyTrainingForm(instance=daily_training)
        return render(request, "RunScheduleApp/daily_training_add.html", {'form': form})

    def post(self, request, plan_id, id):
        daily_training = DailyTraining.objects.get(pk=id)
        form = DailyTrainingForm(request.POST, instance=daily_training)
        if form.is_valid():
            form.save()
            return redirect(f'/plan_details/{plan_id}')
        return render(request, "RunScheduleApp/daily_training_add.html", {'form': form})


class DailyTrainingDelete(View):
    def get(self, request, id):
        daily_training = DailyTraining.objects.get(pk=id)
        if daily_training.workout_plan.owner != get_user(request):
            raise PermissionDenied
        daily_training.delete()
        return redirect(f"/plan_details/{daily_training.workout_plan.id}")


class CurrentWorkoutPlanView(View):
    def get(self, request, month_counter):
        logged_user = get_user(request)
        if logged_user.is_anonymous == True:
            return redirect('/login')
        if not WorkoutPlan.objects.filter(owner=get_user(request)).filter(is_active=True).exists():
            return render(request, "RunScheduleApp/current_workout_plan.html", {'workout_plan': ''})
        workout_plan = WorkoutPlan.objects.filter(owner=get_user(request)).filter(is_active=True)[0]

        plan_start_date = workout_plan.date_range.lower
        plan_end_date = workout_plan.date_range.upper

        first_month_number = plan_start_date.month
        first_year_number = plan_start_date.year
        month_number = first_month_number + int(month_counter)
        year_number = first_year_number
        if month_number > 12:  # mechanizm zmieniający numery miesięcy oraz lat
            year_number = first_year_number + int(month_number / 12)
            month_number = month_number % 12
            if month_number == 0:  # poprawka na grudzień dla którego reszta z dzielenia przez 12 jest zawsze 0
                month_number = 12

        # tworzenie słownika z treningami w danym miesiącu i roku
        trainings = workout_plan.dailytraining_set.filter(day__year=year_number).filter(
            day__month=month_number).order_by('day')
        training_dict = {}
        for training in trainings:
            training_dict.update({f'{training.day.day}': training.name()})

        # pobieramy maksymalny month_counter
        max_month_counter = get_max_month_counter(plan_start_date, plan_end_date)
        present_mont_counter = get_month_counter(plan_start_date)
        cal = WorkoutCalendar(workout_plan, training_dict, month_number, year_number).formatmonth(year_number,
                                                                                                  month_number)

        ctx = {'workout_plan': workout_plan,
               'calendar': mark_safe(cal),
               'month_counter': month_counter,
               'max_month_counter': str(max_month_counter),
               'present_mont_counter': present_mont_counter
               }
        return render(request, "RunScheduleApp/current_workout_plan.html", ctx)


class WorkoutCalendar(HTMLCalendar):

    def __init__(self, workout_plan, training_dict, month_number, year_number):
        super(WorkoutCalendar, self).__init__()
        self.workout_plan = workout_plan
        self.workout_plan_start_date = self.workout_plan.date_range.lower
        self.workout_plan_end_date = self.workout_plan.date_range.upper
        self.training_dict = training_dict
        self.month_number = month_number
        self.year_number = year_number

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        if day == self.workout_plan_start_date.day \
                and self.workout_plan_start_date.month == self.month_number \
                and self.workout_plan_start_date.year == self.year_number:
            return '<td bgcolor= "green" class="%s">%d</td>' % (self.cssclasses[weekday], day)
        if day == self.workout_plan_end_date.day \
                and self.workout_plan_end_date.month == self.month_number \
                and self.workout_plan_end_date.year == self.year_number:
            return '<td bgcolor= "red" class="%s">%d</td>' % (self.cssclasses[weekday], day)
        if str(day) in self.training_dict:
            return '<td bgcolor= "pink" class="%s">%d<br>%s</td>' % (
                self.cssclasses[weekday], day, self.training_dict[str(day)])
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            return '<td class="%s"><a href="%s">%d</a></td>' % (self.cssclasses[weekday], day, day)


####### * * * * * Użytkownicy * * * * * #######

class LoginView(View):

    def get(self, request):
        form = LoginForm()
        return render(request, "RunScheduleApp/login.html", {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("user")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next = request.GET.get("next")
                if next is not None:
                    return redirect(next)
                return redirect("/")
            else:
                return render(request, "RunScheduleApp/login.html", {'form': form})


class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
            return redirect('/')
        else:
            return HttpResponse("Nie jesteś zalogowany")


class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, "RunScheduleApp/registration.html", {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            name = form.cleaned_data.get('name')
            surname = form.cleaned_data.get('surname')
            email = form.cleaned_data.get('email')
            User.objects.create_user(username=username, password=password, email=email, first_name=name,
                                     last_name=surname)
            return redirect('/login')
        return render(request, "RunScheduleApp/registration.html", {'form': form})


class UserProfileView(View):
    def get(self, request):
        return render(request, "RunScheduleApp/user_profile.html")


class PasswordChangeView(View):
    def get(self, request):
        form = PasswordChangeForm()
        return render(request, "RunScheduleApp/password_change.html", {'form': form})

    def post(self, request):
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get("new_password")
            if not request.user.is_authenticated:
                return redirect("/")
            current_user = request.user
            current_user.set_password(new_password)
            current_user.save()
            return redirect("/login")
        return render(request, "RunScheduleApp/password_change.html", {'form': form})


class EditUserView(View):  # TODO dodać edycję profilu uzytkownika
    pass
