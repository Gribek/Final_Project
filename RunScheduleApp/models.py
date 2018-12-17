from django.db import models
from django.contrib.postgres.fields.ranges import DateRangeField
from django.contrib.auth.models import User


# Create your models here.
class WorkoutPlan(models.Model):
    plan_name = models.CharField(max_length=64, verbose_name='Nazwa planu')
    description = models.TextField(null=True, verbose_name='Opis')
    date_range = DateRangeField(verbose_name='Termin')
    is_active = models.BooleanField(default=True, verbose_name='Ustaw jako bieżący')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class DailyTraining(models.Model):
    day = models.DateField()
    description = models.TextField(null=True)
    training_type = models.CharField(max_length=32)
    training_distance = models.SmallIntegerField()
    additional = models.CharField(max_length=32)
    additional_quantity = models.CharField(max_length=32)
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, unique_for_date="day")
    accomplished = models.BooleanField(default=False)

# class TrainingDiary(models.Model): TODO
