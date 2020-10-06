from datetime import datetime, timedelta
from calendar import HTMLCalendar

from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission, User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
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


class WorkoutPlanAddView(PermissionRequiredMixin, View):
    """The class that creates a new workout plan."""

    permission_required = 'RunScheduleApp.add_workoutplan'
    form_class = WorkoutPlanForm
    template_name = 'RunScheduleApp/workout_plan_add.html'

    def get(self, request):
        """Display the form for creating a new workout plan.

        :param request: request object
        :return: form view
        :rtype: HttpResponse
        """
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Create a new workout plan.

        :param request: request object
        :return: list view of all created workouts (if form filled out
            correctly) or form view with error massages
        :rtype: HttpResponse
        """
        form = self.form_class(request.POST)
        user = request.user
        if form.is_valid():
            form.instance.owner = user
            new_plan = form.save()
            if new_plan.is_active:
                set_active_workout_plan(new_plan.id, user)
            return redirect('workout_plans')
        return render(request, self.template_name, {'form': form})


class WorkoutPlanEditView(PermissionRequiredMixin, View):
    """The class that edits an existing workout plan."""

    permission_required = 'RunScheduleApp.change_workoutplan'
    form_class = WorkoutPlanEditForm
    template_name = 'RunScheduleApp/workout_plan_edit.html'

    def get(self, request, plan_id):
        """Display edit form for a selected workout plan.

        :param request: request object
        :param plan_id: id of a workout plan to edit
        :type plan_id: str
        :return: view of the edit form
        :rtype: HttpResponse
        """
        workout_plan = get_object_or_404(WorkoutPlan, pk=plan_id)
        workout_plan.check_owner(request.user)
        form = self.form_class(instance=workout_plan)
        return render(request, self.template_name,
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
        workout_plan = get_object_or_404(WorkoutPlan, pk=plan_id)
        form = self.form_class(request.POST, instance=workout_plan)
        if form.is_valid():
            form.save()
            return redirect('plan_details', plan_id)
        return render(request, self.template_name,
                      {'form': form, 'plan_id': plan_id})


class WorkoutPlanDetailsView(PermissionRequiredMixin, View):
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
        workout_plan = get_object_or_404(WorkoutPlan, pk=plan_id)
        workout_plan.check_owner(request.user)
        date_today = get_today_date()
        ctx = {'workout_plan': workout_plan, 'date_today': date_today}
        return render(request, 'RunScheduleApp/plan_details.html', ctx)


class WorkoutPlanListView(LoginRequiredMixin, View):
    """The class view that shows list of all created workout plans."""

    def get(self, request):
        """Display all user's workout plans.

        :param request: request object
        :return: list view of all workout plans
        :rtype: HttpResponse
        """
        workout_plans = WorkoutPlan.objects.filter(owner=request.user)
        return render(request, 'RunScheduleApp/workout_plan_list.html',
                      {'workout_plans': workout_plans})


class TrainingAddView(PermissionRequiredMixin, View):
    """The class that creates a new training."""

    permission_required = 'RunScheduleApp.add_training'
    form_class = TrainingForm
    template_name = 'RunScheduleApp/training_add.html'

    def get(self, request, plan_id, month=None, year=None, training_date=None):
        """Display the form for creating a new training.

        :param request: request object
        :param plan_id: id of a workout plan to which a new training is
            to be added
        :type plan_id: int
        :param month: month number
        :type month: int
        :param year: year number
        :type year: int
        :param training_date: date of training, optional (default = None)
        :type training_date: str
        :return: form view
        :rtype: HttpResponse
        """
        workout_plan = get_object_or_404(WorkoutPlan, pk=plan_id)
        workout_plan.check_owner(request.user)
        form = self.form_class(initial={'day': training_date,
                                        'plan_id': plan_id})
        ctx = {'form': form, 'plan_id': workout_plan.id,
               'training_date': training_date, 'month_number': month,
               'year_number': year}
        return render(request, self.template_name, ctx)

    def post(self, request, plan_id, month=None, year=None):
        """Create a new training.

        :param request: request object
        :param plan_id: id of a workout plan to which a new training is
            to be added
        :type plan_id: int
        :param month: month number
        :type month: int
        :param year: year number
        :type year: int
        :return: list view of all trainings in a given training plan or
            form view with error massages
        :rtype: HttpResponse
        """
        workout_plan = get_object_or_404(WorkoutPlan, pk=plan_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            form.instance.workout_plan = workout_plan
            form.save()
            if month is None or year is None:
                return redirect('plan_details', plan_id)
            return redirect('current_workout', month, year)
        ctx = {'form': form, 'plan_id': workout_plan.id,
               'month_number': month, 'year_number': year}
        return render(request, self.template_name, ctx)


class TrainingEditView(PermissionRequiredMixin, View):
    """The class that edits an existing training."""

    permission_required = 'RunScheduleApp.change_training'
    form_class = TrainingForm
    template_name = 'RunScheduleApp/training_add.html'

    def get(self, request, plan_id, training_id, month=None, year=None):
        """Display edit form for a selected training.

        :param request: request object
        :param plan_id: id of a workout plan to which a training
            belongs
        :type plan_id: int
        :param training_id: id of a training to edit
        :type training_id: int
        :param month: month number
        :type month: int
        :param year: year number
        :type year: int
        :return: view of the edit form
        :rtype: HttpResponse
        """
        workout_plan = get_object_or_404(WorkoutPlan, pk=plan_id)
        workout_plan.check_owner(request.user)
        training = get_object_or_404(Training, pk=training_id)
        form = self.form_class(instance=training, initial={
            'plan_id': plan_id, 'initial_training_date': training.day})
        ctx = {'form': form, 'plan_id': plan_id, 'month_number': month,
               'year_number': year}
        return render(request, self.template_name, ctx)

    def post(self, request, plan_id, training_id, month=None, year=None):
        """Save changes to a selected training.

        :param request: request object
        :param plan_id: id of a workout plan to which a training
            belongs
        :type plan_id: int
        :param training_id: id of a training to edit
        :type training_id: int
        :param month: month number
        :type month: int
        :param year: year number
        :type year: int
        :return: list view of all trainings in a given training plan
            (if form filled out correctly) or form view with error
            massages
        :rtype: HttpResponse
        """
        training_to_edit = get_object_or_404(Training, pk=training_id)
        form = self.form_class(request.POST, instance=training_to_edit)
        if form.is_valid():
            form.save()
            if month is None or year is None:
                return redirect('plan_details', plan_id)
            return redirect('current_workout', month, year)
        ctx = {'form': form, 'plan_id': plan_id, 'month_number': month,
               'year_number': year}
        return render(request, self.template_name, ctx)


class TrainingDeleteView(PermissionRequiredMixin, View):
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
        training = get_object_or_404(Training, pk=training_id)
        training.workout_plan.check_owner(request.user)
        training.delete()
        return redirect('plan_details', training.workout_plan.id)


class SelectCurrentPlanView(PermissionRequiredMixin, View):
    """The class view for selecting an active workout plan"""

    permission_required = 'RunScheduleApp.view_workoutplan'
    form_class = SelectActivePlanFrom
    template_name = 'RunScheduleApp/select_plan.html'

    def get(self, request):
        """Display the form for selecting an active workout plan.

        :param request: request object
        :return: form view
        :rtype: HttpResponse
        """
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Change the user's active workout plan.

        :param request: request object
        :return: list view of all user plans
        :rtype: HttpResponse
        """
        form = self.form_class(user=request.user, data=request.POST)
        if form.is_valid():
            new_active_plan_id = form.cleaned_data.get('active_plan')
            set_active_workout_plan(new_active_plan_id, request.user)
            return redirect('workout_plans')
        return render(request, self.template_name, {'form': form})


class CurrentWorkoutPlanView(LoginRequiredMixin, View):
    """Display a calendar with training days marked"""

    def get(self, request, month, year):
        """Display a calendar for a given month.

        :param request: request object
        :param month: month number
        :type month: int
        :param year: year number
        :type year: int
        :return: calendar view for the selected month with all
            trainings of active workout plan marked on it
        :rtype: HttpResponse
        """
        workout_plan = CurrentWorkoutPlanView.get_active_workout_plan(
            request.user)
        if not workout_plan:
            return render(request, 'RunScheduleApp/current_workout_plan.html',
                          {'workout_plan': ''})
        start_date, end_date = workout_plan.get_start_and_end_date()
        prev_month, next_month = CurrentWorkoutPlanView.previous_and_next_month(
            workout_plan, month, year)
        calendar = WorkoutCalendar(workout_plan, month, year).formatmonth(
            year, month)
        ctx = {
            'workout_plan': workout_plan,
            'calendar': mark_safe(calendar),
            'prev_month': prev_month,
            'next_month': next_month,
            'start_date': start_date,
            'end_date': end_date
        }
        return render(request, 'RunScheduleApp/current_workout_plan.html',
                      ctx)

    @staticmethod
    def previous_and_next_month(workout_plan, month, year):
        """Calculate previous and next month and year

        :param workout_plan: month number in a workout plan
        :type workout_plan: WorkoutPlan
        :param month: month number
        :type month: int
        :param year: year number
        :type year: int
        :return: month and year number of previous and next month if
            they are part of the plan else None
        :rtype: tuple[dict, dict]
        """
        workout_start, workout_end = workout_plan.get_start_and_end_date()
        today = get_today_date()
        first_day_in_month = today.replace(day=1).replace(month=month).replace(
            year=year)
        last_day_prev_month = first_day_in_month - timedelta(days=1)
        first_day_next_month = (
                first_day_in_month + timedelta(days=32)).replace(day=1)

        if workout_start <= last_day_prev_month:
            prev_month = {'month': last_day_prev_month.month,
                          'year': last_day_prev_month.year}
        else:
            prev_month = None

        if workout_end >= first_day_next_month:
            next_month = {'month': first_day_next_month.month,
                          'year': first_day_next_month.year}
        else:
            next_month = None

        return prev_month, next_month

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

    table_css_class = 'month table calendar'

    def __init__(self, workout_plan, month, year):
        """
        :param workout_plan: workout plan
        :type workout_plan: WorkoutPlan
        :param month: month number
        :type month: int
        :param year: year number
        :type year: int
        """
        super(WorkoutCalendar, self).__init__()
        self.month = month
        self.year = year
        self.workout_plan = workout_plan
        self.workout_plan_start_date, self.workout_plan_end_date = \
            workout_plan.get_start_and_end_date()
        self.training_dict = self.get_trainings_dict()

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

        if day in self.training_dict:  # Training days.
            css_class = self.set_css_class(day, weekday, is_training_day=True)
            link = self.create_training_edit_link(day)
            result = f'<td class="{css_class}"><a href="{link}">{day}' \
                     f'<br><div class="training_info">' \
                     f'{self.training_dict.get(day)}</div></a></td>'
            return result

        else:  # Non-training days.
            css_class = self.set_css_class(day, weekday, is_training_day=False)
            link = self.create_training_add_link(day)
            result = f'<td class="{css_class}"><a href="{link}">{day}' \
                     f'</a></td>'
            return result

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
          % self.table_css_class)
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

    def create_training_add_link(self, day):
        """Create a link to add a training.

        :param day: day number
        :type day: int
        :return: url to add training on a given day
        :rtype: str
        """
        link_date = self.create_date(day)
        link = reverse('add_training_date', args=[
            self.workout_plan.id, self.month, self.year, link_date])
        return link

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
        link = reverse('edit_training_month', args=[
            self.workout_plan.id, training_id, self.month, self.year])
        return link

    def create_date(self, day):
        """Create full date in datetime format.

        :param day: day number
        :return: date
        :rtype: datetime
        """
        full_date = f"{self.year}-{self.month}-{day}"
        return datetime.strptime(full_date, "%Y-%m-%d").date()

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
        full_date = self.create_date(day)
        css_class = self.cssclasses[weekday]
        if full_date == get_today_date():
            return css_class + ' today'
        if full_date == self.workout_plan_start_date:
            return css_class + ' plan_start_day'
        elif full_date == self.workout_plan_end_date:
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
        return {t.day.day: t.training_info() for t in trainings}


class LoginView(View):
    """The class view to log users in."""

    form_class = LoginForm
    template_name = 'RunScheduleApp/login.html'

    def get(self, request):
        """Display login form.

        :param request: request object
        :return: login page view
        :rtype: HttpResponse
        """
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Log a user in.

        :param request: request object
        :return: home page view (if user authenticated correctly) or
            login page view with error massage
        :rtype: HttpResponse
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('user')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if (next_page := request.GET.get('next')) is not None:
                    return redirect(next_page)
                return redirect('home_page')

        return render(request, self.template_name, {'form': form})


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
        return redirect('home_page')


class RegistrationView(View):
    """The class view to register new users."""

    form_class = RegistrationForm
    template_name = 'RunScheduleApp/registration.html'

    def get(self, request):
        """Display registration form.

        :param request: request object
        :return: registration form view
        :rtype: HttpResponse
        """
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Register a new user.

        :param request: request object
        :return: login page view (if form filled out correctly) or
            registration form view with error massages
        :rtype: HttpResponse
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            name = form.cleaned_data.get('name')
            surname = form.cleaned_data.get('surname')
            email = form.cleaned_data.get('email')
            new_user = User.objects.create_user(
                username=username, password=password, email=email,
                first_name=name, last_name=surname)
            permission_list = [
                'add_training', 'change_training',
                'delete_training', 'view_training',
                'add_workoutplan', 'change_workoutplan',
                'delete_workoutplan', 'view_workoutplan',
                'add_trainingdiary', 'change_trainingdiary',
                'view_trainingdiary',
            ]
            p = [Permission.objects.get(codename=i) for i in permission_list]
            new_user.user_permissions.set(p)
            return redirect('login')
        return render(request, self.template_name, {'form': form})


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

    form_class = PasswordChangeForm
    template_name = 'RunScheduleApp/password_change.html'

    def get(self, request):
        """Display a password change form.

        :param request: request object
        :return: password change form view
        :rtype: HttpResponse
        """
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Change user password.

        :param request: request object
        :return: login page view (if form filled out correctly) or
            password change form view with error massage
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            if not request.user.is_authenticated:
                return redirect('login')
            current_user = request.user
            current_user.set_password(new_password)
            current_user.save()
            return redirect('login')
        return render(request, self.template_name, {'form': form})


class EditProfileView(LoginRequiredMixin, View):
    """The class view for changing user data"""

    form_class = EditUserForm
    template_name = 'RunScheduleApp/edit_user_profile.html'

    def get(self, request):
        """Display user data edit form.

        :param request: request object
        :return: user data edit form view
        :rtype: HttpResponse
        """
        current_user = request.user
        form = self.form_class(instance=current_user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Save changes to user data.

        :param request: request object
        :return: user profile page view (if form filled out correctly)
            or user data edit form view with error massages
        :rtype: HttpResponse
        """
        form = self.form_class(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request, self.template_name, {'form': form})


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
    new_active_plan = get_object_or_404(WorkoutPlan, pk=new_active_plan_id)
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


class DiaryEntryAddView(PermissionRequiredMixin, View):
    """The class that creates a new entry to training diary."""

    permission_required = 'RunScheduleApp.add_trainingdiary'
    form_class = DiaryEntryForm
    template_name = 'RunScheduleApp/diary_entry_add.html'

    def get(self, request, training_id):
        """Display the form for creating a new diary entry.

        :param request: request object
        :param training_id: id of a training for which a new entry is
            to be created
        :type training_id: str
        :return: form view
        :rtype: HttpResponse
        """
        training = get_object_or_404(Training, pk=training_id)
        distance = DiaryEntryAddView.calculate_distance(training)
        time = DiaryEntryAddView.calculate_time(training)
        form = self.form_class(initial={
            'date': training.day, 'training_info': training.training_info(),
            'training_distance': distance, 'training_time': time})
        ctx = {'form': form, 'training': training}
        return render(request, self.template_name, ctx)

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
        form = self.form_class(data=request.POST, instance=new_diary_entry)
        training = get_object_or_404(Training, pk=training_id)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            training.accomplished = True
            training.save()
            return redirect('plan_details', training.workout_plan.id)
        ctx = {'form': form, 'training': training}
        return render(request, self.template_name, ctx)

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


def get_today_date():
    """Get today's date

    :return: today's year, month and day
    :rtype: datetime
    """
    return datetime.today().date()
