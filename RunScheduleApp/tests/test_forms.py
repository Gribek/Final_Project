from datetime import timedelta, date

from django.test import TestCase

from RunScheduleApp.forms import DiaryEntryForm, DatePicker
from RunScheduleApp.models import TrainingDiary


class DiaryEntryFormTest(TestCase):
    def setUp(self):
        self.form = DiaryEntryForm()

    def test_form_is_based_on_correct_model(self):
        self.assertEqual(self.form._meta.model, TrainingDiary,
                         'Wrong model assigned in the form')

    def test_form_date_field(self):
        self.assertIn('date', self.form.fields, 'Field missing in form')
        self.assertEqual('Date of training', self.form.fields['date'].label,
                         'Wrong field label')
        self.assertTrue(isinstance(self.form.fields['date'].widget,
                                   DatePicker))

    def test_form_training_info_field(self):
        self.assertIn('training_info', self.form.fields,
                      'Field missing in form')
        self.assertEqual('Training', self.form.fields['training_info'].label,
                         'Wrong field label')

    def test_form_training_distance_field(self):
        self.assertIn('training_distance', self.form.fields,
                      'Field missing in form')
        self.assertEqual(
            'Total distance', self.form.fields['training_distance'].label,
            'Wrong field label')

    def test_form_training_time_field(self):
        self.assertIn('training_time', self.form.fields,
                      'Field missing in form')
        self.assertEqual(
            'Total time', self.form.fields['training_time'].label,
            'Wrong field label')

    def test_form_comments_field(self):
        self.assertIn('comments', self.form.fields, 'Field missing in form')
        self.assertEqual('Comments', self.form.fields['comments'].label,
                         'Wrong field label')

    def test_form_user_field(self):
        self.assertNotIn('user', self.form.fields,
                         'Unnecessary field in the form')

    def test_form_validation_date_incorrect(self):
        date_in_future = date.today() + timedelta(days=1)
        form = DiaryEntryForm(data={
            'date': date_in_future, 'training_info': 'test',
            'training_distance': 10, 'training_time': 60, 'comments': 'test'})
        self.assertFalse(form.is_valid())

    def test_form_validation_date_correct(self):
        date_today = date.today()
        date_in_past = date.today() - timedelta(days=1)
        form = DiaryEntryForm(data={
            'date': date_today, 'training_info': 'test',
            'training_distance': 10, 'training_time': 60, 'comments': 'test'})
        self.assertTrue(form.is_valid())
        form.data['date'] = date_in_past
        self.assertTrue(form.is_valid())
