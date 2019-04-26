from django.test import TestCase
from django.contrib.auth.models import User

from RunScheduleApp.models import Training, WorkoutPlan


class TrainingModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='test user', password='test')
        workout_plan = WorkoutPlan.objects.create(name='setUp plan 1', date_range=["2018-01-01", "2018-01-31"],
                                                  owner=user)
        Training.objects.create(day="2018-04-26", workout_plan=workout_plan, training_main='test main',
                                distance_main=2.5, time_main=30, training_additional='test additional',
                                distance_additional=0.5, time_additional=10)

    def test_creating_training_info(self):
        training = Training.objects.get(id=1)
        expected_training_info = f'{training.training_main} {training.distance_main}km {training.time_main}min ' \
            f'{training.training_additional} {training.distance_additional}km {training.time_additional}min'
        self.assertEqual(expected_training_info, training.training_info())

    def test_object_name_is_training_info(self):
        training = Training.objects.get(id=1)
        self.assertEqual(training.training_info(), str(training))
