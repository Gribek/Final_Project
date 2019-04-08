from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.urls import reverse

from RunScheduleApp.models import WorkoutPlan


class MainPageViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'RunScheduleApp/main_page.html')


class WorkoutsListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(username='test_user', password='test')
        test_user_2 = User.objects.create_user(username='test_user_2', password='test')
        WorkoutPlan.objects.create(plan_name='plan name1', date_range=["2011-01-01", "2018-01-31"], owner=test_user)
        WorkoutPlan.objects.create(plan_name='plan name2', date_range=["2011-01-01", "2018-01-31"], owner=test_user_2)
        WorkoutPlan.objects.create(plan_name='plan name3', date_range=["2011-01-01", "2018-01-31"], owner=test_user)
        WorkoutPlan.objects.create(plan_name='plan name4', date_range=["2011-01-01", "2018-01-31"], owner=test_user_2)
        WorkoutPlan.objects.create(plan_name='plan name5', date_range=["2011-01-01", "2018-01-31"], owner=test_user)

    def test_view_url_exist_at_desired_location(self):
        self.client.login(username='test_user', password='test')
        response = self.client.get('/workout_list')
        self.assertEqual(response.status_code, 200)

    def test_view_redirects_if_not_logged_in(self):
        response = self.client.get('/workout_list')
        self.assertRedirects(response, f'/login?next=/workout_list')

    def test_view_uses_correct_template(self):
        self.client.login(username='test_user', password='test')
        response = self.client.get('/workout_list')
        self.assertTemplateUsed(response, 'RunScheduleApp/workoutplan_list.html')

    def test_view_returns_correct_workout_plans_list_in_context(self):
        self.client.login(username='test_user', password='test')
        response = self.client.get('/workout_list')
        self.assertTrue('workout_plans' in response.context, 'Key not found in context dictionary')
        self.assertEqual(len(response.context['workout_plans']), 3, 'Context does not contain all user plans')
        other_user_workout_plan = WorkoutPlan.objects.get(plan_name='plan name2')
        self.assertFalse(other_user_workout_plan in response.context['workout_plans'],
                         'Context contain workout plan belonging to another user')


class PermissionRequiredViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='user_with_permission', password='test')
        User.objects.create_user(username='non_permission_user', password='test')

    def log_user_with_permission(self):
        self.client.login(username='user_with_permission', password='test')

    def log_non_permission_user(self):
        self.client.login(username='non_permission_user', password='test')


class PlanDetailsViewTest(PermissionRequiredViewTest):
    @classmethod
    def setUpTestData(cls):
        super(PlanDetailsViewTest, cls).setUpTestData()
        user = User.objects.get(username='user_with_permission')
        user.user_permissions.add(Permission.objects.get(codename='view_workoutplan'))
        WorkoutPlan.objects.create(plan_name='name', date_range=["2011-01-01", "2018-01-31"],
                                   owner=User.objects.get(username='user_with_permission'))
        WorkoutPlan.objects.create(plan_name='name', date_range=['2011-01-01', '2018-01-31'],
                                   owner=User.objects.get(username='non_permission_user'))

    def setUp(self):
        self.workout_plan = WorkoutPlan.objects.get(owner__username='user_with_permission')

    def test_view_url_exist_at_desired_location(self):
        self.log_user_with_permission()
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertEqual(response.status_code, 200)

    def test_view_redirects_if_not_logged_in(self):
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertRedirects(response, f'/login?next=/plan_details/{self.workout_plan.id}')

    def test_view_checks_if_user_has_proper_permission(self):
        self.log_non_permission_user()
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertEqual(response.status_code, 403)

    def test_view_checks_if_user_is_owner_of_the_workout_plan(self):
        self.log_user_with_permission()
        response = self.client.get(
            f'/plan_details/{WorkoutPlan.objects.get(owner__username="non_permission_user").id}')
        self.assertEqual(response.status_code, 403)

    def test_view_uses_correct_template(self):
        self.log_user_with_permission()
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertTemplateUsed(response, 'RunScheduleApp/plan_details.html')

    def test_view_returns_workout_plan_object_in_context(self):
        self.log_user_with_permission()
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertTrue('workout_plan' in response.context)
        self.assertEqual(response.context['workout_plan'], self.workout_plan)


class WorkoutPlanAddTest(PermissionRequiredViewTest):

    @classmethod
    def setUpTestData(cls):
        super(WorkoutPlanAddTest, cls).setUpTestData()
        user = User.objects.get(username='user_with_permission')
        user.user_permissions.add(Permission.objects.get(codename='add_workoutplan'))

    def test_view_url_exist_at_desired_location(self):
        self.log_user_with_permission()
        response = self.client.get('/workout_plan_add')
        self.assertEqual(response.status_code, 200)

    def test_view_redirects_if_user_not_logged_in(self):
        response = self.client.get(reverse('workout_plan_add'))
        self.assertTrue(response.url.startswith('/login'))

    def test_view_checks_if_user_has_proper_permission(self):
        self.log_non_permission_user()
        response = self.client.get(reverse('workout_plan_add'))
        self.assertEqual(response.status_code, 403)

    def test_view_uses_correct_template(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('workout_plan_add'))
        self.assertTemplateUsed(response, 'RunScheduleApp/workout_plan_add.html')

    def test_view_returns_form_in_context(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('workout_plan_add'))
        self.assertTrue('form' in response.context, 'Key not found in context dictionary')
