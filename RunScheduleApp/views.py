from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Permission
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


# oblicza max_countera dla ostatniego miesiąca aktualnego planu
def get_max_month_counter(plan_start_date, plan_end_date):
    day_now = datetime.today().date()
    month_max_counter = (plan_end_date.year - day_now.year) * 12 + plan_end_date.month - day_now.month
    month_max_counter += get_month_counter(plan_start_date)
    return month_max_counter


def get_user(request):
    current_user = request.user
    return current_user


class WorkoutPlanAdd(PermissionRequiredMixin, View):
    permission_required = 'RunScheduleApp.add_workoutplan'

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


class WorkoutPlanEdit(PermissionRequiredMixin, View):
    permission_required = 'RunScheduleApp.change_workoutplan'

    def get(self, request, plan_id):
        workout_plan = WorkoutPlan.objects.get(pk=plan_id)
        if workout_plan.owner != get_user(request):
            raise PermissionDenied
        form = WorkoutPlanEditForm(instance=workout_plan)
        return render(request, 'RunScheduleApp/workout_plan_edit.html', {'form': form, 'plan_id': plan_id})

    def post(self, request, plan_id):
        workout_plan = WorkoutPlan.objects.get(pk=plan_id)
        form = WorkoutPlanEditForm(request.POST, instance=workout_plan)
        if form.is_valid():
            form.save()
            return redirect(f'/plan_details/{plan_id}')
        return render(request, 'RunScheduleApp/workout_plan_edit.html', {'form': form, 'plan_id': plan_id})


class PlanDetailsView(PermissionRequiredMixin, View):
    permission_required = 'RunScheduleApp.view_workoutplan'

    def get(self, request, id):
        workout_plan = WorkoutPlan.objects.get(pk=id)
        if workout_plan.owner != get_user(request):
            raise PermissionDenied
        month_counter = get_month_counter(workout_plan.date_range.lower)
        return render(request, "RunScheduleApp/plan_details.html",
                      {'workout_plan': workout_plan, 'month_counter': month_counter})


class WorkoutsList(LoginRequiredMixin, View):
    def get(self, request):
        workout_plans = WorkoutPlan.objects.filter(owner=get_user(request))
        return render(request, "RunScheduleApp/workoutplan_list.html", {'workout_plans': workout_plans})


def get_plan_start_and_end_date(workout_plan):
    start_date = workout_plan.date_range.lower
    end_date = workout_plan.date_range.upper
    return end_date, start_date


class DailyTrainingAdd(PermissionRequiredMixin, View):
    permission_required = 'RunScheduleApp.add_dailytraining'

    def get(self, request, id, date=None):
        if date is not None:
            date_format = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            date_format = None
        workout_plan = WorkoutPlan.objects.get(pk=id)
        if workout_plan.owner != get_user(request):
            return HttpResponse('Nie możesz dodać treningu do nie swojego planu!')
        end_date, start_date = get_plan_start_and_end_date(workout_plan)
        form = DailyTrainingForm(initial={'day': date_format, 'start_date': start_date, 'end_date': end_date})
        return render(request, "RunScheduleApp/daily_training_add.html", {'form': form, 'plan_id': workout_plan.id})

    def post(self, request, id, date=None):
        new_training = DailyTraining()
        form = DailyTrainingForm(request.POST, instance=new_training)
        workout_plan = WorkoutPlan.objects.get(pk=id)
        if form.is_valid():
            workout = WorkoutPlan.objects.get(pk=id)
            form.instance.workout_plan = workout
            form.save()
            return redirect(f'/plan_details/{id}')
        # return HttpResponse('Not valid')
        return render(request, "RunScheduleApp/daily_training_add.html", {'form': form, 'plan_id': workout_plan.id})


class DailyTrainingEdit(PermissionRequiredMixin, View):
    permission_required = 'RunScheduleApp.change_dailytraining'

    def get(self, request, plan_id, id):
        workout_plan = WorkoutPlan.objects.get(pk=plan_id)
        if workout_plan.owner != get_user(request):
            raise PermissionDenied
        daily_training = DailyTraining.objects.get(pk=id)
        end_date, start_date = get_plan_start_and_end_date(workout_plan)
        form = DailyTrainingForm(instance=daily_training, initial={'start_date': start_date, 'end_date': end_date})
        return render(request, "RunScheduleApp/daily_training_add.html", {'form': form, 'plan_id': plan_id})

    def post(self, request, plan_id, id):
        daily_training = DailyTraining.objects.get(pk=id)
        form = DailyTrainingForm(request.POST, instance=daily_training)
        if form.is_valid():
            form.save()
            return redirect(f'/plan_details/{plan_id}')
        return render(request, "RunScheduleApp/daily_training_add.html", {'form': form, 'plan_id': plan_id})


class DailyTrainingDelete(PermissionRequiredMixin, View):
    permission_required = 'RunScheduleApp.delete_dailytraining'

    def get(self, request, id):
        daily_training = DailyTraining.objects.get(pk=id)
        if daily_training.workout_plan.owner != get_user(request):
            raise PermissionDenied
        daily_training.delete()
        return redirect(f"/plan_details/{daily_training.workout_plan.id}")


class SelectActivePlanView(PermissionRequiredMixin, View):
    permission_required = 'RunScheduleApp.view_workoutplan'

    def get_user_plans_tuple(self, request):
        all_user_plans = WorkoutPlan.objects.filter(owner=request.user)
        plan_name_array = []
        plan_id_array = []
        for plan in all_user_plans:
            plan_id_array.append(plan.plan_name)
            plan_name_array.append(plan.id)
        return tuple(zip(plan_name_array, plan_id_array))

    def get(self, request):
        PLANS_TUPLE = self.get_user_plans_tuple(request)
        form = SelectActivePlanFrom(choices=PLANS_TUPLE)
        return render(request, "RunScheduleApp/select_plan.html", {'form': form})

    def post(self, request):
        PLANS_TUPLE = self.get_user_plans_tuple(request)
        form = SelectActivePlanFrom(request.POST, choices=PLANS_TUPLE)
        if form.is_valid():
            new_active_plan_id = form.cleaned_data.get('active_plan')
            WorkoutPlan.objects.filter(owner=request.user).filter(is_active=True).update(is_active=False)
            new_active_plan = WorkoutPlan.objects.get(pk=new_active_plan_id)
            new_active_plan.is_active = True
            new_active_plan.save()
            return redirect("/workout_list")
        return render(request, "RunScheduleApp/select_plan.html", {'form': form})


class CurrentWorkoutPlanView(LoginRequiredMixin, View):
    def get(self, request, month_counter):
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

        # tworzenie słownika z treningami w danym miesiącu danego roku
        trainings = workout_plan.dailytraining_set.filter(day__year=year_number).filter(
            day__month=month_number).order_by('day')
        training_dict = {}
        for training in trainings:
            training_dict.update({f'{training.day.day}': training.name()})

        # pobieramy maksymalny month_counter i lucznik dla aktualnego miesiąca
        max_month_counter = get_max_month_counter(plan_start_date, plan_end_date)
        present_mont_counter = get_month_counter(plan_start_date)

        # Wywołujemy klase WorkoutCalendar, dziedziczącą po HTMLCalendar, którego metody zostały nadpisane
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
    cssclass_month = "month table"
    # day_abbr = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Nd"]

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
        # dzień początkowy treningu
        if day == self.workout_plan_start_date.day \
                and self.workout_plan_start_date.month == self.month_number \
                and self.workout_plan_start_date.year == self.year_number:
            if str(day) in self.training_dict:
                edit_day_link = self.create_day_edit_link(day)
                return '<td bgcolor= "greenyellow" class="%s"><a href="%s">%d</a><br>%s</td>' % (
                    self.cssclasses[weekday], edit_day_link, day, self.training_dict[str(day)])
            else:
                date = self.create_date_string(day)
                edit_day_link = f"/daily_training_add/{self.workout_plan.id}/{date}"
                return '<td bgcolor= "greenyellow" class="%s"><a href="%s">%d</a></td>' % (
                    self.cssclasses[weekday], edit_day_link, day)
        # dzień końcowy treningu
        if day == self.workout_plan_end_date.day \
                and self.workout_plan_end_date.month == self.month_number \
                and self.workout_plan_end_date.year == self.year_number:
            if str(day) in self.training_dict:
                edit_day_link = self.create_day_edit_link(day)
                return '<td bgcolor= "#ff6666" class="%s"><a href="%s">%d</a><br>%s</td>' % (
                    self.cssclasses[weekday], edit_day_link, day, self.training_dict[str(day)])
            else:
                date = self.create_date_string(day)
                edit_day_link = f"/daily_training_add/{self.workout_plan.id}/{date}"
                return '<td bgcolor= "#ff6666" class="%s"><a href="%s">%d</a></td>' % (
                    self.cssclasses[weekday], edit_day_link, day)
        # obsługuje pola w tabeli "poza" miesiącem
        if day == 0:
            return '<td class="noday">&nbsp;</td>'
        # dni treningowe
        if str(day) in self.training_dict:
            edit_day_link = self.create_day_edit_link(day)
            return '<td bgcolor= "#798EF6" class="%s"><a href="%s">%d<br>%s</a></td>' % (
                self.cssclasses[weekday], edit_day_link, day, self.training_dict[str(day)])
        # dni nietreningowe
        else:
            date = self.create_date_string(day)
            edit_day_link = f"/daily_training_add/{self.workout_plan.id}/{date}"
            return '<td class="%s"><a href="%s">%d</a></td>' % (self.cssclasses[weekday], edit_day_link, day)

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        v = []
        a = v.append
        a(
            '<table id="fixedheight" style="table-layout: fixed" border="0" cellpadding="0" cellspacing="0" class="%s">' % (
                self.cssclass_month))
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)

    # def formatweekday(self, day):
    #     # Return a weekday name as a table header.
    #     return '<th class="%s">%s</th>' % (self.cssclasses[day], self.day_abbr[day])

    def create_day_edit_link(self, day):
        date = self.create_date_string(day)  # buduje pełną datę tego elementu
        date_format = datetime.strptime(date, "%Y-%m-%d").date()  # zamienia ją na typ datetime,date
        edit_day_id = DailyTraining.objects.get(day=date_format).id  # pobieramy trening obecny pod tą datą
        edit_day_link = f"/daily_training_edit/{self.workout_plan.id}/{edit_day_id}"  # tworzymy link do edycji
        return edit_day_link

    def create_date_string(self, day):
        date = f"{self.year_number}-{self.month_number}-{day}"  # buduje pełną datę tego elementu
        return date


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
            new_user = User.objects.get(username=username)
            permission_list = [
                'add_dailytraining',
                'change_dailytraining',
                'delete_dailytraining',
                'view_dailytraining',
                'add_workoutplan',
                'change_workoutplan',
                'delete_workoutplan',
                'view_workoutplan',
            ]
            permissions = [Permission.objects.get(codename=i) for i in
                           permission_list]  # tworzymy listę objektów typu permission !!!
            new_user.user_permissions.set(permissions)
            return redirect('/login')
        return render(request, "RunScheduleApp/registration.html", {'form': form})


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "RunScheduleApp/user_profile.html")


class PasswordChangeView(LoginRequiredMixin, View):
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


class EditUserView(LoginRequiredMixin, View):
    def get(self, request):
        current_user = request.user
        form = EditUserForm(instance=current_user)
        return render(request, "RunScheduleApp/edit_user_profile.html", {'form': form})

    def post(self, request):
        form = EditUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("/profile")
        return render(request, "RunScheduleApp/edit_user_profile.html", {'form': form})
