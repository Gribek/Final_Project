from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
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


class PlanDetailsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='user_with_permission', password='test')
        user.user_permissions.add(Permission.objects.get(codename='view_workoutplan'))
        User.objects.create_user(username='user_without_permission', password='test')
        WorkoutPlan.objects.create(plan_name='plan name', date_range=["2011-01-01", "2018-01-31"],
                                   owner=User.objects.get(username='user_with_permission'))
        WorkoutPlan.objects.create(plan_name='name', date_range=['2011-01-01', '2018-01-31'],
                                   owner=User.objects.get(username='user_without_permission'))

    def setUp(self):
        self.workout_plan = WorkoutPlan.objects.get(owner__username='user_with_permission')

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertNotEqual(response.status_code, 404)

    def test_view_checks_if_user_has_proper_permission(self):
        self.client.login(username='user_with_permission', password='test')
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertEqual(response.status_code, 200)

    def test_view_checks_if_user_without_proper_permission_get_code_403(self):
        self.client.login(username='user_without_permission', password='test')
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertEqual(response.status_code, 403)

    def test_view_checks_if_user_is_owner_of_the_workout_plan(self):
        self.client.login(username='user_with_permission', password='test')
        response = self.client.get(
            f'/plan_details/{WorkoutPlan.objects.get(owner__username="user_without_permission").id}')
        self.assertEqual(response.status_code, 403)

    def test_view_uses_correct_template(self):
        self.client.login(username='user_with_permission', password='test')
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertTemplateUsed(response, 'RunScheduleApp/plan_details.html')

    def test_view_redirects_if_not_logged_in(self):
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertRedirects(response, f'/login?next=/plan_details/{self.workout_plan.id}')

    def test_view_returns_workout_plan_object_in_context(self):
        self.client.login(username='user_with_permission', password='test')
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertTrue('workout_plan' in response.context)
        self.assertEqual(response.context['workout_plan'], self.workout_plan)


class WorkoutsList(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='test_user', password='test')
        user_2 = User.objects.create_user(username='test_user_2', password='test')
        WorkoutPlan.objects.create(plan_name='plan name1', date_range=["2011-01-01", "2018-01-31"], owner=user)
        WorkoutPlan.objects.create(plan_name='plan name2', date_range=["2011-01-01", "2018-01-31"], owner=user_2)
        WorkoutPlan.objects.create(plan_name='plan name3', date_range=["2011-01-01", "2018-01-31"], owner=user)
        WorkoutPlan.objects.create(plan_name='plan name4', date_range=["2011-01-01", "2018-01-31"], owner=user_2)
        WorkoutPlan.objects.create(plan_name='plan name5', date_range=["2011-01-01", "2018-01-31"], owner=user)

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get('/workout_list')
        self.assertNotEqual(response.status_code, 404, 'Url does not exist')

    def test_view_checks_if_user_is_logged_in(self):
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
        self.assertEqual(len(response.context['workout_plans']), 3, 'Context does not contain all users plans')
        other_user_workout_plan = WorkoutPlan.objects.get(plan_name='plan name2')
        self.assertFalse(other_user_workout_plan in response.context['workout_plans'],
                         'Context contain workout plan belongs to other user')
