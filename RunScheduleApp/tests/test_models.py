from django.test import TestCase
from django.contrib.auth.models import User

from RunScheduleApp.models import Training, WorkoutPlan, TrainingDiary


class TrainingModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='test user', password='test')
        workout_plan = WorkoutPlan.objects.create(
            name='setUp plan 1', date_range=["2018-01-01", "2018-01-31"],
            owner=user)
        Training.objects.create(
            day="2018-04-26", workout_plan=workout_plan,
            training_main='test main', distance_main=2.5, time_main=30,
            training_additional='test additional',distance_additional=0.5,
            time_additional=10)

    def test_creating_training_info(self):
        training = Training.objects.get(id=1)
        expected = f'{training.training_main} {training.distance_main}km ' \
            f'{training.time_main}min {training.training_additional} ' \
            f'{training.distance_additional}km {training.time_additional}min'
        self.assertEqual(expected, training.training_info())

    def test_object_name_is_training_info(self):
        training = Training.objects.get(id=1)
        self.assertEqual(training.training_info(), str(training))


class TrainingDiaryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='test user', password='test')
        TrainingDiary.objects.create(
            training_info='Test diary training entry', training_distance=10.5,
            training_time=80, user=user, comments='comment test',
            date='2018-01-01')

    def setUp(self):
        self.diary_entry = TrainingDiary.objects.get(
            training_info='Test diary training entry')

    def test_creating_new_training_diary_object(self):
        self.assertTrue(isinstance(self.diary_entry, TrainingDiary))

    def test_date_field(self):
        field_label = self.diary_entry._meta.get_field('date').verbose_name
        self.assertEqual(field_label, 'Date')

    def test_training_info_field(self):
        model_field = self.diary_entry._meta.get_field('training_info')
        field_label = model_field.verbose_name
        max_length = model_field.max_length
        self.assertEqual(field_label, 'Training')
        self.assertEqual(max_length, 128)

    def test_training_distance_field(self):
        model_field = self.diary_entry._meta.get_field('training_distance')
        field_label = model_field.verbose_name
        max_digits = model_field.max_digits
        decimal_places = model_field.decimal_places
        self.assertEqual(field_label, 'Total distance')
        self.assertEqual(max_digits, 3)
        self.assertEqual(decimal_places, 1)

    def test_training_time_field(self):
        label = self.diary_entry._meta.get_field('training_time').verbose_name
        self.assertEqual(label, 'Total time')

    def test_comments_field(self):
        model_field = self.diary_entry._meta.get_field('comments')
        field_label = model_field.verbose_name
        max_length = model_field.max_length
        self.assertEqual(field_label, 'Comments')
        self.assertEqual(max_length, 256)
        self.assertTrue(model_field.null)
        self.assertTrue(model_field.blank)
