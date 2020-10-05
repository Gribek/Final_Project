from datetime import date

from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.urls import reverse

from RunScheduleApp.models import WorkoutPlan, Training, TrainingDiary
from RunScheduleApp.forms import DiaryEntryForm
from RunScheduleApp.views import DiaryEntryAddView


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
        user_1 = User.objects.create_user(
            username='user_with_permission', password='test')
        user_2 = User.objects.create_user(
            username='non_permission_user', password='test')
        WorkoutPlan.objects.create(
            name='setUp plan 1', date_range=["2011-01-01", "2018-01-31"],
            owner=user_1, is_active=True)
        WorkoutPlan.objects.create(
            name='setUp plan 2', date_range=["2011-01-01", "2018-01-31"],
            owner=user_2, is_active=False)
        WorkoutPlan.objects.create(
            name='setUp plan 3', date_range=["2011-01-01", "2018-01-31"],
            owner=user_1)
        WorkoutPlan.objects.create(
            name='setUp plan 4', date_range=["2011-01-01", "2018-01-31"],
            owner=user_1)
        WorkoutPlan.objects.create(
            name='setUp plan 5', date_range=["2011-01-01", "2018-01-31"],
            owner=user_2)

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
        self.assertTemplateUsed(response,
                                'RunScheduleApp/workout_plan_list.html')

    def test_view_returns_correct_workout_plans_list_in_context(self):
        self.log_user_with_permission()
        response = self.client.get('/workout_list')
        self.assertIn('workout_plans', response.context,
                      'Key not found in context dictionary')
        number_of_user_plans = WorkoutPlan.objects.filter(
            owner__username='user_with_permission').count()
        self.assertEqual(
            len(response.context['workout_plans']), number_of_user_plans,
            'Context does not contain all user plans')
        other_users_workout_plans = WorkoutPlan.objects.exclude(
            owner__username='user_with_permission')
        self.assertTrue(
            all([plan not in response.context['workout_plans']
                 for plan in other_users_workout_plans]),
            'Context contain workout plan belonging to another user')


class PlanDetailsViewTest(PermissionRequiredViewTest):
    @classmethod
    def setUpTestData(cls):
        super(PlanDetailsViewTest, cls).setUpTestData()
        user = User.objects.get(username='user_with_permission')
        user.user_permissions.add(Permission.objects.get(
            codename='view_workoutplan'))

    def setUp(self):
        self.workout_plan = WorkoutPlan.objects.get(name='setUp plan 1')

    def test_view_url_exist_at_desired_location(self):
        self.log_user_with_permission()
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertEqual(response.status_code, 200)

    def test_view_redirects_if_not_logged_in(self):
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertRedirects(
            response, f'/login?next=/plan_details/{self.workout_plan.id}')

    def test_view_checks_if_user_has_proper_permission(self):
        self.log_non_permission_user()
        response = self.client.get(f'/plan_details/{self.workout_plan.id}')
        self.assertEqual(response.status_code, 403)

    def test_view_checks_if_user_is_owner_of_the_workout_plan(self):
        self.log_user_with_permission()
        other_user_workout_plan = WorkoutPlan.objects.get(name='setUp plan 2')
        response = self.client.get(
            f'/plan_details/{other_user_workout_plan.id}')
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
        user.user_permissions.add(Permission.objects.get(
            codename='add_workoutplan'))

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
        self.assertTemplateUsed(response,
                                'RunScheduleApp/workout_plan_add.html')

    def test_view_returns_form_in_context(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('workout_plan_add'))
        self.assertIn('form', response.context,
                      'Key not found in context dictionary')

    def test_view_checks_if_workout_plan_is_created_in_post(self):
        self.log_user_with_permission()
        number_of_workout_plans = WorkoutPlan.objects.count()
        data = {'name': 'new plan', 'date_range_0': '2011-01-01',
                'date_range_1': '2018-01-01'}
        response = self.client.post(reverse('workout_plan_add'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/workout_list')
        self.assertEqual(WorkoutPlan.objects.count(),
                         number_of_workout_plans + 1)

    def test_view_returns_the_form_if_data_not_valid(self):
        self.log_user_with_permission()
        data = {'name': 'new plan', 'date_range_0': '2020-01-01',
                'date_range_1': '2018-01-01'}
        response = self.client.post(reverse('workout_plan_add'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'RunScheduleApp/workout_plan_add.html')

    def test_view_checks_if_workout_plan_is_correctly_set_as_active(self):
        self.log_user_with_permission()
        data = {'name': 'new plan', 'date_range_0': '2011-01-01',
                'date_range_1': '2018-01-01', 'is_active': True}
        self.client.post(reverse('workout_plan_add'), data)
        self.assertTrue(WorkoutPlan.objects.get(name='new plan').is_active,
                        'Workout plan not set as active')
        self.assertEqual(WorkoutPlan.objects.filter(is_active=True).count(),
                         1, 'More than one active workout plan')


class WorkoutPlanEditTest(PermissionRequiredViewTest):
    @classmethod
    def setUpTestData(cls):
        super(WorkoutPlanEditTest, cls).setUpTestData()
        user = User.objects.get(username='user_with_permission')
        user.user_permissions.set(
            [Permission.objects.get(codename='change_workoutplan'),
             Permission.objects.get(codename='view_workoutplan')])

    def setUp(self):
        self.workout_plan = WorkoutPlan.objects.create(
            name='plan to edit', date_range=["2011-01-01", "2018-01-31"],
            owner=User.objects.get(username='user_with_permission'))

    def test_view_url_exist_at_desired_location(self):
        self.log_user_with_permission()
        response = self.client.get(
            f'/workout_plan_edit/{self.workout_plan.id}')
        self.assertEqual(response.status_code, 200)

    def test_view_redirects_if_user_not_logged_in(self):
        response = self.client.get(reverse('workout_plan_edit', kwargs={
            'plan_id': self.workout_plan.id}))
        self.assertTrue(response.url.startswith('/login'))

    def test_view_checks_if_user_has_proper_permission(self):
        self.log_non_permission_user()
        response = self.client.get(reverse('workout_plan_edit', kwargs={
            'plan_id': self.workout_plan.id}))
        self.assertEqual(response.status_code, 403)

    def test_view_uses_correct_template(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('workout_plan_edit', kwargs={
            'plan_id': self.workout_plan.id}))
        self.assertTemplateUsed(response,
                                'RunScheduleApp/workout_plan_edit.html')

    def test_view_returns_form_with_data_and_plan_id_in_context(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('workout_plan_edit', kwargs={
            'plan_id': self.workout_plan.id}))
        self.assertIn('form', response.context,
                      'Key "form" not found in context dictionary')
        self.assertEqual(response.context['form'].initial['name'],
                         self.workout_plan.name, 'No initial data')
        self.assertIn('plan_id', response.context,
                      'Key "plan_id" not found in context dictionary')
        self.assertEqual(response.context['plan_id'],
                         str(self.workout_plan.id), 'Wrong plan id value')

    def test_view_checks_if_user_is_owner_of_the_workout_plan(self):
        self.log_user_with_permission()
        other_user_workout_plan = WorkoutPlan.objects.get(name='setUp plan 2')
        response = self.client.get(
            f'/plan_details/{other_user_workout_plan.id}')
        self.assertEqual(response.status_code, 403)

    def test_view_checks_if_workout_plan_is_edited_in_post(self):
        self.log_user_with_permission()
        data = {'name': 'changed plan name', 'date_range_0': '2010-01-01',
                'date_range_1': '2020-01-31'}
        response = self.client.post(reverse('workout_plan_edit', kwargs={
            'plan_id': self.workout_plan.id}), data)
        changed_workout_plan = WorkoutPlan.objects.get(
            id=self.workout_plan.id)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response,
                             f'/plan_details/{self.workout_plan.id}')
        self.assertEqual(changed_workout_plan.name, 'changed plan name')
        self.assertEqual(changed_workout_plan.date_range.lower,
                         date(2010, 1, 1))
        self.assertEqual(changed_workout_plan.date_range.upper,
                         date(2020, 1, 31))

    def test_view_returns_the_form_if_data_not_valid(self):
        self.log_user_with_permission()
        data = {'name': 'changed plan name', 'date_range_0': '2020-01-01',
                'date_range_1': '2010-01-31'}
        response = self.client.post(reverse('workout_plan_edit', kwargs={
            'plan_id': self.workout_plan.id}), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'RunScheduleApp/workout_plan_edit.html')


class TrainingDiaryViewTest(PermissionRequiredViewTest):
    @classmethod
    def setUpTestData(cls):
        super(TrainingDiaryViewTest, cls).setUpTestData()
        user = User.objects.get(username='user_with_permission')
        other_user = User.objects.get(username='non_permission_user')
        user.user_permissions.add(Permission.objects.get(
            codename='view_trainingdiary'))
        TrainingDiary.objects.create(
            date='2019-03-01', training_info='test training info',
            training_distance=12.5, training_time=70,
            comments='test comments', user=user)
        TrainingDiary.objects.create(
            date='2019-03-03', training_info='test training info',
            training_distance=12.5, training_time=70,
            comments='test comments', user=user)
        TrainingDiary.objects.create(
            date='2019-03-07', training_info='test training info',
            training_distance=12.5, training_time=70,
            comments='test comments', user=user)
        TrainingDiary.objects.create(
            date='2019-03-10', training_info='test training info',
            training_distance=12.5, training_time=70,
            comments='test comments', user=user)
        TrainingDiary.objects.create(
            date='2019-03-20', training_info='test training info',
            training_distance=12.5, training_time=70,
            comments='test comments', user=other_user)
        TrainingDiary.objects.create(
            date='2019-03-30', training_info='test training info',
            training_distance=12.5, training_time=70,
            comments='test comments', user=other_user)

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get('/training_diary')
        self.assertNotEqual(response.status_code, 404)

    def test_view_redirects_if_user_not_logged_in(self):
        response = self.client.get('/training_diary')
        self.assertTrue(response.url.startswith('/login'))

    def test_view_url_has_name_attribute(self):
        response = self.client.get(reverse('training_diary'))
        self.assertTrue(response.status_code)

    def test_view_checks_if_user_has_proper_permission(self):
        self.log_non_permission_user()
        response = self.client.get(reverse('training_diary'))
        self.assertEqual(response.status_code, 403)

    def test_view_uses_correct_template(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('training_diary'))
        self.assertTemplateUsed(response,
                                'RunScheduleApp/training_diary_view.html')

    def test_view_returns_correct_diary_entries_in_context(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('training_diary'))
        self.assertIn('diary_entries', response.context,
                      'Key not found in context dictionary')
        number_of_entries = TrainingDiary.objects.filter(
            user__username='user_with_permission').count()
        self.assertEqual(len(response.context['diary_entries']),
                         number_of_entries,
                         'Context does not contain all user plans')
        other_users_entries = TrainingDiary.objects.exclude(
            user__username='user_with_permission')
        self.assertTrue(all(entry not in response.context['diary_entries']
                            for entry in other_users_entries),
                        'Context contains entries belonging to other user')

    def test_view_diary_entries_sorted_ascending_by_date(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('training_diary'))
        entries = response.context['diary_entries']
        self.assertTrue(all([entries[i - 1].date < entries[i].date
                             for i in range(1, len(entries))]))


class TrainingDiaryEntryAddTest(PermissionRequiredViewTest):
    @classmethod
    def setUpTestData(cls):
        super(TrainingDiaryEntryAddTest, cls).setUpTestData()
        user = User.objects.get(username='user_with_permission')
        user.user_permissions.set(
            [Permission.objects.get(codename='add_trainingdiary'),
             Permission.objects.get(codename='view_workoutplan')])
        workout_plan = WorkoutPlan.objects.get(name='setUp plan 1')
        Training.objects.create(
            day='2018-01-01', training_main='test training 1',
            distance_main=10, time_main=60, training_additional='8x100m',
            workout_plan=workout_plan)
        Training.objects.create(
            day='2018-01-01', training_main='test training 2',
            distance_additional=20, time_additional=50,
            training_additional='8x100m', workout_plan=workout_plan)
        Training.objects.create(
            day='2018-01-01', training_main='test training 3',
            training_additional='8x100m', workout_plan=workout_plan)
        Training.objects.create(
            day='2018-01-01', training_main='test training 4',
            distance_main=10, time_main=60, training_additional='8x100m',
            distance_additional=5, time_additional=20,
            workout_plan=workout_plan)

    def setUp(self):
        self.training = Training.objects.get(training_main='test training 1')

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get(
            f'/training_diary_entry_add/{self.training.id}')
        self.assertNotEqual(response.status_code, 404)

    def test_view_redirects_if_user_not_logged_in(self):
        response = self.client.get(
            f'/training_diary_entry_add/{self.training.id}')
        self.assertTrue(response.url.startswith('/login'))

    def test_view_url_has_name_attribute(self):
        response = self.client.get(reverse('diary_entry_add', kwargs={
            'training_id': self.training.id}))
        self.assertTrue(response.status_code)

    def test_view_checks_if_user_has_proper_permission(self):
        self.log_non_permission_user()
        response = self.client.get(reverse('diary_entry_add', kwargs={
            'training_id': self.training.id}))
        self.assertEqual(response.status_code, 403)

    def test_view_uses_correct_template(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('diary_entry_add', kwargs={
            'training_id': self.training.id}))
        self.assertTemplateUsed(response,
                                'RunScheduleApp/diary_entry_add.html')

    def test_view_returns_correct_form_in_context(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('diary_entry_add', kwargs={
            'training_id': self.training.id}))
        self.assertIn('form', response.context,
                      'Form not found in context dictionary')
        self.assertTrue(isinstance(response.context['form'], DiaryEntryForm),
                        'Wrong form returned in context')

    def test_view_form_filed_with_initial_data(self):
        self.log_user_with_permission()
        response = self.client.get(reverse('diary_entry_add', kwargs={
            'training_id': self.training.id}))
        form = response.context['form']
        self.assertEqual(form.initial['date'], self.training.day,
                         'No date in initial data')
        self.assertEqual(form.initial['training_info'],
                         self.training.training_info(),
                         'No training_info in initial data')
        distance = DiaryEntryAddView.calculate_distance(self.training)
        self.assertEqual(form.initial['training_distance'], distance,
                         'No training_distance in initial data')
        time = DiaryEntryAddView.calculate_time(self.training)
        self.assertEqual(form.initial['training_time'], time,
                         'No training_time in initial data')

    def test_view_diary_entry_created_in_post(self):
        self.log_user_with_permission()
        number_of_diary_entries = TrainingDiary.objects.count()
        data = {'date': '2018-01-01', 'training_info': 'test training info',
                'training_distance': 8.5, 'training_time': 70,
                'comments': 'test comment'}
        response = self.client.post(reverse('diary_entry_add', kwargs={
            'training_id': self.training.id}), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(number_of_diary_entries + 1,
                         TrainingDiary.objects.count())
        self.assertRedirects(response,
                             f'/plan_details/{self.training.workout_plan.id}')

    def test_view_returns_the_form_if_data_not_valid(self):
        self.log_user_with_permission()
        data = {'date': '2120-01-01', 'training_info': 'test training info',
                'training_distance': 8.5, 'training_time': 70,
                'comments': 'test comment'}
        response = self.client.post(reverse('diary_entry_add', kwargs={
            'training_id': self.training.id}), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'RunScheduleApp/diary_entry_add.html',
            'Wrong template used')
        self.assertIn('form', response.context,
                      'No form in context dictionary')
        self.assertTrue(isinstance(response.context['form'], DiaryEntryForm),
                        'Wrong form returned in context')

    def test_view_set_training_as_accomplished(self):
        self.log_user_with_permission()
        data = {'date': '2018-01-01', 'training_info': 'test training info',
                'training_distance': 8.5, 'training_time': 70,
                'comments': 'test comment'}
        self.client.post(reverse('diary_entry_add', kwargs={
            'training_id': self.training.id}), data)
        training = Training.objects.get(id=self.training.id)
        self.assertTrue(training.accomplished)

    def test_calculate_distance_and_calculate_time_methods(self):
        training_1 = Training.objects.get(training_main='test training 1')
        training_2 = Training.objects.get(training_main='test training 2')
        training_3 = Training.objects.get(training_main='test training 3')
        training_4 = Training.objects.get(training_main='test training 4')
        distance_1 = DiaryEntryAddView.calculate_distance(training_1)
        distance_2 = DiaryEntryAddView.calculate_distance(training_2)
        distance_3 = DiaryEntryAddView.calculate_distance(training_3)
        distance_4 = DiaryEntryAddView.calculate_distance(training_4)
        time_1 = DiaryEntryAddView.calculate_time(training_1)
        time_2 = DiaryEntryAddView.calculate_time(training_2)
        time_3 = DiaryEntryAddView.calculate_time(training_3)
        time_4 = DiaryEntryAddView.calculate_time(training_4)
        self.assertEqual(distance_1, 10, 'Wrong distance')
        self.assertEqual(distance_2, 20, 'Wrong distance')
        self.assertEqual(distance_3, None, 'Wrong distance')
        self.assertEqual(distance_4, 15, 'Wrong distance')
        self.assertEqual(time_1, 60, 'Wrong time')
        self.assertEqual(time_2, 50, 'Wrong time')
        self.assertEqual(time_3, None, 'Wrong time')
        self.assertEqual(time_4, 80, 'Wrong time')
