from datetime import datetime
from calendar import HTMLCalendar

from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission, User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.views import View

from RunScheduleApp.forms import *
from RunScheduleApp.models import WorkoutPlan, Training


class MainPageView(View):
    """Class view for the application's home page."""

    def get(self, request):
        """Display application's home page.

        :param request: request object
        :return: home page view
        :rtype: HttpResponse
        """
        return render(request, 'RunScheduleApp/main_page.html')


class WorkoutPlanAdd(PermissionRequiredMixin, View):
    """The class that creates a new workout plan."""

    permission_required = 'RunScheduleApp.add_workoutplan'

    def get(self, request):
        """Display the form for creating a new workout plan.

        :param request: request object
        :return: form view
        :rtype: HttpResponse
        """
        form = WorkoutPlanForm()
        return render(request, 'RunScheduleApp/workout_plan_add.html',
                      {'form': form})

    def post(self, request):
        """Create a new workout plan.

        :param request: request object
        :return: list view of all created workouts (if form filled out
            correctly) or form view with error massages
        :rtype: HttpResponse
        """
        new_workout_plan = WorkoutPlan()
        form = WorkoutPlanForm(request.POST, instance=new_workout_plan)
        if form.is_valid():
            form.instance.owner = request.user
            new_plan = form.save()
            if form.instance.is_active:
                set_active_workout_plan(new_plan.id, request.user)
            return redirect('/workout_list')
        return render(request, 'RunScheduleApp/workout_plan_add.html',
                      {'form': form})


class WorkoutPlanEdit(PermissionRequiredMixin, View):
    """The class that edits an existing workout plan."""

    permission_required = 'RunScheduleApp.change_workoutplan'

    def get(self, request, plan_id):
        """Display edit form for a selected workout plan.

        :param request: request object
        :param plan_id: id of a workout plan to edit
        :type plan_id: str
        :return: view of the edit form
        :rtype: HttpResponse
        """
        workout_plan = WorkoutPlan.objects.get(pk=plan_id)
        check_workout_plan_owner(workout_plan, request.user)
        form = WorkoutPlanEditForm(instance=workout_plan)
        return render(request, 'RunScheduleApp/workout_plan_edit.html',
                      {'form': form, 'plan_id': plan_id})

    def post(self, request, plan_id):
        """Save changes to a selected workout plan.

        :param request: request object
        :param plan_id: id of a workout plan to edit
        :type plan_id: str
        :return: plan details view (if form filled out correctly) or
            form view with error massages
        :rtype: HttpResponse
        """
        workout_plan = WorkoutPlan.objects.get(pk=plan_id)
        form = WorkoutPlanEditForm(request.POST, instance=workout_plan)
        if form.is_valid():
            form.save()
            return redirect(f'/plan_details/{plan_id}')
        return render(request, 'RunScheduleApp/workout_plan_edit.html',
                      {'form': form, 'plan_id': plan_id})


class PlanDetailsView(PermissionRequiredMixin, View):
    """The class view that shows information about a workout plan."""

    permission_required = 'RunScheduleApp.view_workoutplan'

    def get(self, request, plan_id):
        """Display information about a selected workout plan.

        :param request: request object
        :param plan_id: workout plan id
        :type plan_id: str
        :return: view of the workout plan details
        :rtype: HttpResponse
        """
        workout_plan = WorkoutPlan.objects.get(pk=plan_id)
        check_workout_plan_owner(workout_plan, request.user)
        date_today = datetime.today().date()
        ctx = {'workout_plan': workout_plan, 'date_today': date_today}
        return render(request, 'RunScheduleApp/plan_details.html', ctx)


class WorkoutsList(LoginRequiredMixin, View):
    """The class view that shows list of all created workout plans."""

    def get(self, request):
        """Display all user's workout plans.

        :param request: request object
        :return: list view of all workout plans
        :rtype: HttpResponse
        """
        workout_plans = WorkoutPlan.objects.filter(owner=request.user)
        return render(request, 'RunScheduleApp/workoutplan_list.html',
                      {'workout_plans': workout_plans})


class TrainingAdd(PermissionRequiredMixin, View):
    """The class that creates a new training."""

    permission_required = 'RunScheduleApp.add_training'

    def get(self, request, plan_id, month_number=None, date=None):
        """Display the form for creating a new training.

        :param request: request object
        :param plan_id: id of a workout plan to which a new training is
            to be added
        :type plan_id: str
        :param month_number: month number according to workout plan
            numbering
        :type month_number: str
        :param date: date of training, optional (default = None)
        :type date: str
        :return: form view
        :rtype: HttpResponse
        """
        workout_plan = WorkoutPlan.objects.get(pk=plan_id)
        check_workout_plan_owner(workout_plan, request.user)
        start_date, end_date = get_plan_start_and_end_date(workout_plan)
        form = TrainingForm(initial={'day': date, 'start_date': start_date,
                                     'end_date': end_date})
        ctx = {'form': form, 'plan_id': workout_plan.id,
               'date': date, 'month_number': month_number}
        return render(request, 'RunScheduleApp/training_add.html', ctx)

    def post(self, request, plan_id, month_number=None):
        """Create a new training.

        :param request: request object
        :param plan_id: id of a workout plan to which a new training is
            to be added
        :type plan_id: str
        :param month_number: month number according to workout plan
            numbering
        :type month_number: str
        :return: list view of all trainings in a given training plan or
            form view with error massages
        :rtype: HttpResponse
        """
        new_training = Training()
        form = TrainingForm(request.POST, instance=new_training)
        workout_plan = WorkoutPlan.objects.get(pk=plan_id)
        if form.is_valid():
            workout = WorkoutPlan.objects.get(pk=plan_id)
            form.instance.workout_plan = workout
            form.save()
            if month_number is None:
                return redirect(f'/plan_details/{plan_id}')
            return redirect(f'/workout/{month_number}')
        ctx = {'form': form, 'plan_id': workout_plan.id,
               'month_number': month_number}
        return render(request, 'RunScheduleApp/training_add.html', ctx)


class TrainingEdit(PermissionRequiredMixin, View):
    """The class that edits an existing training."""

    permission_required = 'RunScheduleApp.change_training'

    def get(self, request, plan_id, training_id, month_number=None):
        """Display edit form for a selected training.

        :param request: request object
        :param plan_id: id of a workout plan to which a training
            belongs
        :type plan_id: str
        :param training_id: id of a training to edit
        :type training_id: str
        :param month_number: month number according to workout plan
            numbering
        :type month_number: str
        :return: view of the edit form
        :rtype: HttpResponse
        """
        workout_plan = WorkoutPlan.objects.get(pk=plan_id)
        check_workout_plan_owner(workout_plan, request.user)
        training_to_edit = Training.objects.get(pk=training_id)
        start_date, end_date = get_plan_start_and_end_date(workout_plan)
        form = TrainingForm(instance=training_to_edit, initial={
            'start_date': start_date, 'end_date': end_date})
        ctx = {'form': form, 'plan_id': plan_id, 'month_number': month_number}
        return render(request, 'RunScheduleApp/training_add.html', ctx)

    def post(self, request, plan_id, training_id, month_number=None):
        """Save changes to a selected training.

        :param request: request object
        :param plan_id: id of a workout plan to which a training
            belongs
        :type plan_id: str
        :param training_id: id of a training to edit
        :type training_id: str
        :param month_number: month number according to workout plan
            numbering
        :type month_number: str
        :return: list view of all trainings in a given training plan
            (if form filled out correctly) or form view with error
            massages
        :rtype: HttpResponse
        """
        training_to_edit = Training.objects.get(pk=training_id)
        form = TrainingForm(request.POST, instance=training_to_edit)
        if form.is_valid():
            form.save()
            if month_number is None:
                return redirect(f'/plan_details/{plan_id}')
            return redirect(f'/workout/{month_number}')
        ctx = {'form': form, 'plan_id': plan_id, 'month_number': month_number}
        return render(request, 'RunScheduleApp/training_add.html', ctx)


class TrainingDelete(PermissionRequiredMixin, View):
    """The class that deletes an existing training."""

    permission_required = 'RunScheduleApp.delete_training'

    def get(self, request, training_id):
        """Delete a selected training.

        :param request: request object
        :param training_id: id of a training to delete
        :type training_id: str
        :return: list view of all remaining trainings in a training
            plan to which the deleted training belonged
        :rtype: HttpResponse
        """
        training_to_delete = Training.objects.get(pk=training_id)
        check_workout_plan_owner(training_to_delete.workout_plan,
                                 request.user)
        training_to_delete.delete()
        return redirect(f'/plan_details/{training_to_delete.workout_plan.id}')


class SelectActivePlanView(PermissionRequiredMixin, View):
    """The class view for selecting an active workout plan"""

    permission_required = 'RunScheduleApp.view_workoutplan'

    @staticmethod
    def get_user_plans(request):
        """Get all training plans belonging to the current user.

        :param request: request object
        :return: a tuple of paired workout plan ids with workout plan
            names
        :rtype: tuple[tuple[int, str]]
        """
        all_user_plans = WorkoutPlan.objects.filter(owner=request.user)
        plan_name_array = []
        plan_id_array = []
        for plan in all_user_plans:
            plan_id_array.append(plan.name)
            plan_name_array.append(plan.id)
        return tuple(zip(plan_name_array, plan_id_array))

    def get(self, request):
        """Display the form for selecting an active workout plan.

        :param request: request object
        :return: form view
        :rtype: HttpResponse
        """
        plans_tuple = SelectActivePlanView.get_user_plans(request)
        form = SelectActivePlanFrom(choices=plans_tuple)
        return render(request, 'RunScheduleApp/select_plan.html',
                      {'form': form})

    def post(self, request):
        """Change the user's active workout plan.

        :param request: request object
        :return: list view of all user plans
        :rtype: HttpResponse
        """
        plans_tuple = SelectActivePlanView.get_user_plans(request)
        form = SelectActivePlanFrom(request.POST, choices=plans_tuple)
        if form.is_valid():
            new_active_plan_id = form.cleaned_data.get('active_plan')
            set_active_workout_plan(new_active_plan_id, request.user)
            return redirect('/workout_list')
        return render(request, 'RunScheduleApp/select_plan.html',
                      {'form': form})


class WorkoutPlanView(LoginRequiredMixin, View):
    """The class view displaying a calendar with training marked.

    Within that class, all variables and methods names containing the
    phrase 'month_number' refers to the numbers of the following months
    in a workout plan. Number of the first month in a workout plan is
    equal to 1. Number of the second month is 2, the third is 3, etc.
    """

    def get(self, request, month_number_requested):
        """Display a calendar for a given month.

        :param request: request object
        :param month_number_requested: month number in a workout plan
        :type month_number_requested: str
        :return: calendar view for the selected month with all
            trainings of active workout plan marked on it
        :rtype: HttpResponse
        """
        workout_plan = WorkoutPlanView.get_active_workout_plan(request.user)
        if not workout_plan:
            return render(request, 'RunScheduleApp/current_workout_plan.html',
                          {'workout_plan': ''})
        plan_start_date, plan_end_date = get_plan_start_and_end_date(
            workout_plan)
        present_month_number = WorkoutPlanView.get_present_month_number(
            plan_start_date)
        last_month_number = WorkoutPlanView.get_last_month_number(
            plan_start_date, plan_end_date)

        month, year = WorkoutPlanView.get_month_and_year(
            month_number_requested, plan_start_date)
        calendar = WorkoutCalendar(workout_plan, month, year,
                                   month_number_requested).formatmonth(year,
                                                                       month)

        ctx = {
            'workout_plan': workout_plan,
            'calendar': mark_safe(calendar),
            'month_number_requested': month_number_requested,
            'last_month_number': str(last_month_number),
            'present_month_number': present_month_number
        }
        return render(request, 'RunScheduleApp/current_workout_plan.html',
                      ctx)

    @staticmethod
    def get_month_and_year(month_number_requested, plan_start_date):
        """Calculate month and year for formatmonth method.

        :param month_number_requested: month number in a workout plan
        :type month_number_requested: str
        :param plan_start_date: workout plan start date
        :type plan_start_date: datetime
        :return: number of month and year
        :rtype: tuple[int, int]
        """
        plan_first_month = plan_start_date.month
        plan_first_year = plan_start_date.year
        month = plan_first_month + int(month_number_requested) - 1
        year = plan_first_year

        if month > 12:  # For plans exceeding a calendar year.
            year = plan_first_year + int(month / 12)
            month = month % 12
            if month == 0:  # Amendment for december, when % 12 == 0
                month = 12
                year -= 1
        return month, year

    @staticmethod
    def get_last_month_number(start_date, end_date):
        """Calculate month number for the last month in workout plan.

        :param start_date: first day of a plan
        :type start_date: datetime
        :param end_date: last day of a plan
        :type end_date: datetime
        :return: month number for the last month of a plan
        :rtype: int
        """
        last_month_number = ((end_date.year - start_date.year) * 12
                             + end_date.month - start_date.month + 1)
        return last_month_number

    @staticmethod
    def get_present_month_number(plan_start_date):
        """Calculate month number for present month (according to date).

        :param plan_start_date: first day of a plan
        :type plan_start_date: datetime
        :return: month number of the present month in workout plan
        :rtype: int
        """
        day_now = datetime.today().date()
        month_number = ((day_now.year - plan_start_date.year) * 12
                        + day_now.month - plan_start_date.month + 1)
        return month_number

    @staticmethod
    def get_active_workout_plan(user):
        """Get user's active workout plan.

        :param user: user, owner of a workout plan
        :type user: User
        :return: active workout plan for the user or None if it does
            not exist
        :rtype: WorkoutPlan or None
        """
        workout_plan = WorkoutPlan.objects.filter(owner=user).filter(
            is_active=True)
        if workout_plan.exists():
            return workout_plan[0]
        else:
            return None


class WorkoutCalendar(HTMLCalendar):
    """A class used to create monthly workout calendar in HTML"""

    css_class_month = 'month table calendar'

    def __init__(self, workout_plan, month, year, month_number_requested):
        """
        :param workout_plan: workout plan
        :type workout_plan: WorkoutPlan
        :param month: month number
        :type month: int
        :param year: year number
        :type year: int
        :param month_number_requested: month number according to
            workout plan numbering
        :type month_number_requested: str
        """
        super(WorkoutCalendar, self).__init__()
        self.month = month
        self.year = year
        self.workout_plan = workout_plan
        self.workout_plan_start_date, self.workout_plan_end_date = \
            get_plan_start_and_end_date(workout_plan)
        self.training_dict = self.get_trainings_dict()
        self.month_number_requested = month_number_requested

    def formatday(self, day, weekday):
        """Return a day as a table cell.

        :param day: day number
        :type day: int
        :param weekday: day of the week (numbers from 0 to 6, 0 means
            monday, 6 means sunday)
        :type weekday: int
        :return: HTML code for one day
        :rtype: str
        """
        if day == 0:  # Table cells for days 'outside' the month.
            return '<td class="noday">&nbsp;</td>'

        if str(day) in self.training_dict:  # Training days.
            css_class = self.set_css_class(day, weekday, is_training_day=True)
            edit_training_link = self.create_training_edit_link(day)
            return '<td class="%s"><a href="%s">%d<br>' \
                   '<div class="training_info">%s</div></a></td>' % (
                       css_class, edit_training_link, day,
                       self.training_dict[str(day)])

        else:  # Non-training days.
            css_class = self.set_css_class(day, weekday, is_training_day=False)
            link_date = self.create_date(day)
            add_training_link = f"/training_add/{self.workout_plan.id}/" \
                                f"{self.month_number_requested}/{link_date}"
            return '<td class="%s"><a href="%s">%d</a></td>' % (
                css_class, add_training_link, day)

    def formatmonth(self, theyear, themonth, withyear=True):
        """Return a formatted month as a table.

        :param theyear: year number
        :type theyear: int
        :param themonth: month number
        :type themonth: int
        :param withyear: if True year number will be included in table
            header, optional (default = True)
        :type withyear: bool
        :return: HTML code for whole month
        :rtype: str
        """
        v = []
        a = v.append
        a('<table id="fixedheight" style="table-layout: fixed" border="0"'
          ' cellpadding="0" cellspacing="0" class="%s">'
          % self.css_class_month)
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

    def create_training_edit_link(self, day):
        """Create a link to edit a training.

        :param day: day number
        :type day: int
        :return: url to edit training on a given day
        :rtype: str
        """
        link_date = self.create_date(day)
        training_id = Training.objects.filter(
            workout_plan=self.workout_plan).get(day=link_date).id
        edit_day_link = f'/training_edit/{self.workout_plan.id}/{training_id}/' \
                        f'{self.month_number_requested}'
        return edit_day_link

    def create_date(self, day):
        """Create full date in datatime format.

        :param day: day number
        :return: date
        :rtype: datetime
        """
        date = f"{self.year}-{self.month}-{day}"
        date_format_datetime = datetime.strptime(date, "%Y-%m-%d").date()
        return date_format_datetime

    def set_css_class(self, day, weekday, is_training_day):
        """Set css classes for table cell.

        :param day: day number
        :type day: int
        :param weekday: weekday: day of the week (numbers from 0 to 6,
            0 means monday, 6 means sunday)
        :type weekday: int
        :param is_training_day: indicates if there is a training in
            that day
        :type is_training_day: bool
        :return: background color
        :rtype: str
        """
        date = self.create_date(day)
        css_class = self.cssclasses[weekday]
        if date == datetime.today().date():
            return css_class + ' today'
        if date == self.workout_plan_start_date:
            return css_class + ' plan_start_day'
        elif date == self.workout_plan_end_date:
            return css_class + ' plan_end_day'
        if is_training_day:
            return css_class + ' training_day'
        else:
            return css_class

    def get_trainings_dict(self):
        """Create dictionary with trainings.

        :return: information about trainings in formatted month,
            day number as key and information about training in that
            day as value
        :rtype: dict[str, str]
        """
        trainings = self.workout_plan.training_set.filter(
            day__year=self.year).filter(day__month=self.month).order_by('day')
        t_dict = {}
        for training in trainings:
            t_dict.update({f'{training.day.day}': training.training_info()})
        return t_dict


class LoginView(View):
    """The class view to log users in."""

    def get(self, request):
        """Display login form.

        :param request: request object
        :return: login page view
        :rtype: HttpResponse
        """
        form = LoginForm()
        return render(request, 'RunScheduleApp/login.html', {'form': form})

    def post(self, request):
        """Log a user in.

        :param request: request object
        :return: home page view (if user authenticated correctly) or
            login page view with error massage
        :rtype: HttpResponse
        """
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('user')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next = request.GET.get('next')
                if next is not None:
                    return redirect(next)
                return redirect('/')
            else:
                return render(request, 'RunScheduleApp/login.html',
                              {'form': form})
        return render(request, 'RunScheduleApp/login.html', {'form': form})


class LogoutView(View):
    """The class view to log users out."""

    def get(self, request):
        """Log a user out.

        :param request: request object
        :return: home page view
        :rtype: HttpResponse
        """
        if request.user.is_authenticated:
            logout(request)
        return redirect('/')


class RegistrationView(View):
    """The class view to register new users."""

    def get(self, request):
        """Display registration form.

        :param request: request object
        :return: registration form view
        :rtype: HttpResponse
        """
        form = RegistrationForm()
        return render(request, 'RunScheduleApp/registration.html',
                      {'form': form})

    def post(self, request):
        """Register a new user.

        :param request: request object
        :return: login page view (if form filled out correctly) or
            registration form view with error massages
        :rtype: HttpResponse
        """
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            name = form.cleaned_data.get('name')
            surname = form.cleaned_data.get('surname')
            email = form.cleaned_data.get('email')
            User.objects.create_user(username=username, password=password,
                                     email=email, first_name=name,
                                     last_name=surname)
            new_user = User.objects.get(username=username)
            permission_list = [
                'add_training',
                'change_training',
                'delete_training',
                'view_training',
                'add_workoutplan',
                'change_workoutplan',
                'delete_workoutplan',
                'view_workoutplan',
                'add_trainingdiary',
                'change_trainingdiary',
                'view_trainingdiary',
            ]
            p = [Permission.objects.get(codename=i) for i in permission_list]
            new_user.user_permissions.set(p)
            return redirect('/login')
        return render(request, 'RunScheduleApp/registration.html',
                      {'form': form})


class UserProfileView(LoginRequiredMixin, View):
    """The class view that shows information about user"""

    def get(self, request):
        """Display user profile.

        :param request: request object
        :return: user profile page view
        :rtype: HttpResponse
        """
        return render(request, 'RunScheduleApp/user_profile.html')


class PasswordChangeView(LoginRequiredMixin, View):
    """The class view for changing user password"""

    def get(self, request):
        """Display a password change form.

        :param request: request object
        :return: password change form view
        :rtype: HttpResponse
        """
        form = PasswordChangeForm()
        return render(request, 'RunScheduleApp/password_change.html',
                      {'form': form})

    def post(self, request):
        """Change user password.

        :param request: request object
        :return: login page view (if form filled out correctly) or
            password change form view with error massage
        """
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            if not request.user.is_authenticated:
                return redirect('/')
            current_user = request.user
            current_user.set_password(new_password)
            current_user.save()
            return redirect('/login')
        return render(request, 'RunScheduleApp/password_change.html',
                      {'form': form})


class EditUserView(LoginRequiredMixin, View):
    """The class view for changing user data"""

    def get(self, request):
        """Display user data edit form.

        :param request: request object
        :return: user data edit form view
        :rtype: HttpResponse
        """
        current_user = request.user
        form = EditUserForm(instance=current_user)
        return render(request, 'RunScheduleApp/edit_user_profile.html',
                      {'form': form})

    def post(self, request):
        """Save changes to user data.

        :param request: request object
        :return: user profile page view (if form filled out correctly)
            or user data edit form view with error massages
        :rtype: HttpResponse
        """
        form = EditUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/profile')
        return render(request, 'RunScheduleApp/edit_user_profile.html',
                      {'form': form})


def get_plan_start_and_end_date(workout_plan):
    """Get workout plan start and end date.

    :param workout_plan: workout plan
    :type workout_plan: WorkoutPlan
    :return: workout plan start date and end date
    :rtype: tuple[datetime, datetime]
    """
    start_date = workout_plan.date_range.lower
    end_date = workout_plan.date_range.upper
    return start_date, end_date


def check_workout_plan_owner(workout_plan, user):
    """Check if user is owner of given workout plan.

    :param workout_plan: workout plan
    :type workout_plan: WorkoutPlan
    :param user: user
    :type user: User
    :return: confirmation of ownership
    :rtype: bool
    """
    if workout_plan.owner != user:
        raise PermissionDenied


def set_active_workout_plan(new_active_plan_id, user):
    """Set workout plan as active.

    :param new_active_plan_id: id of a workout plan to be set as active
    :type new_active_plan_id: str or int
    :param user: user for whom new active plan is to be set
    :type user: User
    :return: None
    """
    WorkoutPlan.objects.filter(owner=user).filter(is_active=True).update(
        is_active=False)
    new_active_plan = WorkoutPlan.objects.get(pk=new_active_plan_id)
    new_active_plan.is_active = True
    new_active_plan.save()
    return None


class TrainingDiaryView(PermissionRequiredMixin, View):
    """The class view that shows entries in training diary."""

    permission_required = 'RunScheduleApp.view_trainingdiary'

    def get(self, request):
        """Display user's training diary.

        :param request: request object
        :return: view of training diary belonging to logged user
        :rtype: HttpResponse
        """
        user = User.objects.get(id=request.user.id)
        diary_entries = user.trainingdiary_set.all().order_by('date')
        return render(request, 'RunScheduleApp/training_diary_view.html',
                      {'diary_entries': diary_entries})


class TrainingDiaryEntryAdd(PermissionRequiredMixin, View):
    """The class that creates a new entry to training diary."""

    permission_required = 'RunScheduleApp.add_trainingdiary'

    def get(self, request, training_id):
        """Display the form for creating a new diary entry.

        :param request: request object
        :param training_id: id of a training for which a new entry is
            to be created
        :type training_id: str
        :return: form view
        :rtype: HttpResponse
        """
        training = Training.objects.get(id=training_id)
        distance = TrainingDiaryEntryAdd.calculate_distance(training)
        time = TrainingDiaryEntryAdd.calculate_time(training)
        form = DiaryEntryForm(initial={
            'date': training.day, 'training_info': training.training_info(),
            'training_distance': distance, 'training_time': time})
        return render(request, 'RunScheduleApp/diary_entry_add.html',
                      {'form': form})

    def post(self, request, training_id):
        """Create a new diary entry.

        :param request: request object
        :param training_id: id of a training for which a new entry is
            to be created
        :type training_id: str
        :return: training diary view or form view with error massages
        :rtype: HttpResponse
        """
        new_diary_entry = TrainingDiary()
        form = DiaryEntryForm(data=request.POST, instance=new_diary_entry)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            training = Training.objects.get(id=training_id)
            training.accomplished = True
            training.save()
            return redirect(f'/plan_details/{training.workout_plan.id}')
        return render(request, 'RunScheduleApp/diary_entry_add.html',
                      {'form': form})

    @staticmethod
    def calculate_distance(training):
        """Calculate the distance for a given training.

        :param training: training
        :type training: Training
        :return: sum of all distances or nothing if there are none
        :rtype: decimal or None
        """
        if training.distance_main and training.distance_additional:
            distance = training.distance_main + training.distance_additional
        elif training.distance_main:
            distance = training.distance_main
        elif training.distance_additional:
            distance = training.distance_additional
        else:
            distance = None
        return distance

    @staticmethod
    def calculate_time(training):
        """Calculate duration of a given training.

        :param training: training
        :type training: Training
        :return: duration of training
        :rtype: int or None
        """
        if training.time_main and training.time_additional:
            time = training.time_main + training.time_additional
        elif training.time_main:
            time = training.time_main
        elif training.time_additional:
            time = training.time_additional
        else:
            time = None
        return time
