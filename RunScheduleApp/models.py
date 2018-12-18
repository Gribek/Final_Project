from django.db import models
from django.contrib.postgres.fields.ranges import DateRangeField
from django.contrib.auth.models import User


# Create your models here.
class WorkoutPlan(models.Model):
    plan_name = models.CharField(max_length=64, verbose_name='Nazwa planu')
    description = models.TextField(null=True, verbose_name='Opis', blank=True)
    date_range = DateRangeField(verbose_name='Termin')
    is_active = models.BooleanField(default=False, verbose_name='Ustaw jako bieżący')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class DailyTraining(models.Model):
    day = models.DateField(verbose_name='Wybierz datę')
    description = models.TextField(null=True, verbose_name='Dodatkowy opis', blank=True)
    training_type = models.CharField(max_length=32, verbose_name='Rodzaj treningu')
    training_distance = models.SmallIntegerField(verbose_name='Dystans (km)')
    additional = models.CharField(null=True, max_length=32, verbose_name="Dodatkowo", blank=True)
    additional_quantity = models.CharField(null=True, max_length=32, verbose_name="Ilość", blank=True)
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, unique_for_date=day,
                                     verbose_name="Dodaj trening do planu")
    accomplished = models.BooleanField(default=False)

    def name(self):
        t_info = f"{self.training_type} {self.training_distance}km"
        t_info += f" {self.additional} {self.additional_quantity}" if self.additional else ""
        return t_info

    def __str__(self):
        return self.name()

# class TrainingDiary(models.Model): TODO
