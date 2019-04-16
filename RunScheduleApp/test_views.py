from datetime import date

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


class PermissionRequiredViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_1 = User.objects.create_user(username='user_with_permission', password='test')
        user_2 = User.objects.create_user(username='non_permission_user', password='test')
        WorkoutPlan.objects.create(name='setUp plan 1', date_range=["2011-01-01", "2018-01-31"], owner=user_1,
                                   is_active=True)
        WorkoutPlan.objects.create(name='setUp plan 2', date_range=["2011-01-01", "2018-01-31"], owner=user_2,
                                   is_active=False)
        WorkoutPlan.objects.create(name='setUp plan 3', date_range=["2011-01-01", "2018-01-31"], owner=user_1)
        WorkoutPlan.objects.create(name='setUp plan 4', date_range=["2011-01-01", "2018-01-31"], owner=user_1)
        WorkoutPlan.objects.create(name='setUp plan 5', date_range=["2011-01-01", "2018-01-31"], owner=user_2)

    def log_user_with_permission(self):
        self.client.login(username='user_with_permission', password='test')

    def log_non_permission_user(self):
        self.client.login(username='non_permission_user', password='test')


class WorkoutsListTest(PermissionRequiredViewTest):
    def test_view_url_exist_at_desired_location(self):
        self.log_user_with_permission()
        response = self.client.get('/workout_list')
        self.assertEqual(response.status_code, 200)

    def test_view_redirects_if_not_logged_in(self):
        response = self.client.get('/workout_list')
        self.assertRedirects(response, f'/login?next=/workout_list')

    def test_view_uses_correct_template(self):
        self.log_user_with_permission()
        response = self.client.get('/workout_list')
        self.assertTemplateUsed(response, 'RunScheduleApp/workoutplan_list.html')

    def test_view_returns_correct_workout_plans_list_in_context(self):
        self.log_user_with_permission()
        response = self.client.get('/workout_list')
        self.assertTrue('workout_plans' in response.context, 'Key not found in context dictionary')
        number_of_user_plans = len(WorkoutPlan.objects.filter(owner__username='user_with_permission'))
        self.assertEqual(len(response.context['workout_plans']), number_of_user_plans,
                         'Context does not contain all user plans')
        other_user_workout_plan = WorkoutPlan.objects.get(name='setUp plan 2')
        self.assertFalse(other_user_workout_plan in response.context['workout_plans'],
                         'Context contain workout plan belonging to another user')


class PlanDetailsViewTest(PermissionRequiredViewTest):
    @classmethod
    def setUpTestData(cls):
        super(PlanDetailsViewTest, cls).setUpTestData()
        user = User.objects.get(username='user_with_permission')
        user.user_permissions.add(Permission.objects.get(codename='view_workoutplan'))

    def setUp(self):
        self.workout_plan = WorkoutPlan.objects.get(name='setUp plan 1')

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
        other_user_workout_plan = WorkoutPlan.objects.get(name='setUp plan 2')
        response = self.client.get(f'/plan_details/{other_user_workout_plan.id}')
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

    def test_view_checks_if_workout_plan_is_created_in_post(self):
        self.log_user_with_permission()
        number_of_workout_plans = WorkoutPlan.objects.count()
        data = {'name': 'new plan', 'date_range_0': '2011-01-01', 'date_range_1': '2018-01-01'}
        response = self.client.post(reverse('workout_plan_add'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/workout_list')
        self.assertEqual(WorkoutPlan.objects.count(), number_of_workout_plans + 1)

    def test_view_returns_the_form_if_data_not_valid(self):
        self.log_user_with_permission()
        data = {'name': 'new plan', 'date_range_0': '2020-01-01', 'date_range_1': '2018-01-01'}
        response = self.client.post(reverse('workout_plan_add'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'RunScheduleApp/workout_plan_add.html')

    def test_view_checks_if_workout_plan_is_set_as_active(self):
        self.log_user_with_permission()
        data = {'name': 'new plan', 'date_range_0': '2011-01-01',
                'date_range_1': '2018-01-01', 'is_active': True}
        self.client.post(reverse('workout_plan_add'), data)
        self.assertTrue(WorkoutPlan.objects.get(name='new plan').is_active)
        self.assertFalse(WorkoutPlan.objects.get(name='setUp plan 1').is_active)


class WorkoutPlanEditTest(PermissionRequiredViewTest):
    @classmethod
    def setUpTestData(cls):
        super(WorkoutPlanEditTest, cls).setUpTestData()
        user = User.objects.get(username='user_with_permission')
        user.user_permissions.set([Permission.objects.get(codename='change_workoutplan'),
                                   Permission.objects.get(codename='view_workoutplan')])

    def setUp(self):
        self.workout_plan = WorkoutPlan.objects.create(name='plan to edit',
                                                       date_range=["2011-01-01", "2018-01-31"],
                                                       owner=User.objects.get(username='user_with_permission'))

    def test_view_url_exist_at_desired_location(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('workout_plan_edit', kwargs={'plan_id': self.workout_plan.id}))
        self.assertEqual(response.status_code, 200)

    def test_view_redirects_if_user_not_logged_in(self):
        response = self.client.get(reverse('workout_plan_edit', kwargs={'plan_id': self.workout_plan.id}))
        self.assertTrue(response.url.startswith('/login'))

    def test_view_checks_if_user_has_proper_permission(self):
        self.log_non_permission_user()
        response = self.client.get(reverse('workout_plan_edit', kwargs={'plan_id': self.workout_plan.id}))
        self.assertEqual(response.status_code, 403)

    def test_view_uses_correct_template(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('workout_plan_edit', kwargs={'plan_id': self.workout_plan.id}))
        self.assertTemplateUsed(response, 'RunScheduleApp/workout_plan_edit.html')

    def test_view_returns_form_with_data_and_plan_id_in_context(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('workout_plan_edit', kwargs={'plan_id': self.workout_plan.id}))
        self.assertTrue('form' in response.context, 'Key "form" not found in context dictionary')
        self.assertEqual(response.context['form'].initial['name'], self.workout_plan.name, 'No initial data')
        self.assertTrue('plan_id' in response.context, 'Key "plan_id" not found in context dictionary')
        self.assertEqual(response.context['plan_id'], str(self.workout_plan.id), 'Wrong plan id value')

    def test_view_checks_if_user_is_owner_of_the_workout_plan(self):
        self.log_user_with_permission()
        other_user_workout_plan = WorkoutPlan.objects.get(name='setUp plan 2')
        response = self.client.get(f'/plan_details/{other_user_workout_plan.id}')
        self.assertEqual(response.status_code, 403)

    def test_view_checks_if_workout_plan_is_edited_in_post(self):
        self.log_user_with_permission()
        data = {'name': 'changed plan name', 'date_range_0': '2010-01-01',
                'date_range_1': '2020-01-31'}
        response = self.client.post(reverse('workout_plan_edit', kwargs={'plan_id': self.workout_plan.id}), data)
        changed_workout_plan = WorkoutPlan.objects.get(id=self.workout_plan.id)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/plan_details/{self.workout_plan.id}')
        self.assertEqual(changed_workout_plan.name, 'changed plan name')
        self.assertEqual(changed_workout_plan.date_range.lower, date(2010, 1, 1))
        self.assertEqual(changed_workout_plan.date_range.upper, date(2020, 1, 31))

    def test_view_returns_the_form_if_data_not_valid(self):
        self.log_user_with_permission()
        data = {'name': 'changed plan name', 'date_range_0': '2020-01-01',
                'date_range_1': '2010-01-31'}
        response = self.client.post(reverse('workout_plan_edit', kwargs={'plan_id': self.workout_plan.id}), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'RunScheduleApp/workout_plan_edit.html')
