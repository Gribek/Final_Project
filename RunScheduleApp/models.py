from django.db import models
from django.contrib.postgres.fields.ranges import DateRangeField
from django.contrib.auth.models import User


class WorkoutPlan(models.Model):
    """Stores a single workout plan entry."""

    name = models.CharField(max_length=64, verbose_name='Name of the plan')
    description = models.TextField(null=True, verbose_name='Description',
                                   blank=True)
    date_range = DateRangeField(verbose_name='Time range')
    is_active = models.BooleanField(default=False,
                                    verbose_name='Set as current')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_start_and_end_date(self):
        """Get workout plan start date and end date.

        :return: workout plan start date and end date
        :rtype: tuple[datetime, datetime]
        """
        return self.date_range.lower, self.date_range.upper


class Training(models.Model):
    """Stores a single training entry."""

    day = models.DateField(verbose_name='Date of training')
    training_main = models.CharField(
        max_length=32, verbose_name='Main training')
    distance_main = models.DecimalField(
        max_digits=3, decimal_places=1, verbose_name='Distance [km]',
        null=True, blank=True)
    time_main = models.SmallIntegerField(
        verbose_name='Time [min]', null=True, blank=True)
    training_additional = models.CharField(
        null=True, max_length=32, blank=True,
        verbose_name='Additional training (optional)')
    distance_additional = models.DecimalField(
        max_digits=3, decimal_places=1, verbose_name='Distance [km]',
        null=True, blank=True)
    time_additional = models.SmallIntegerField(
        verbose_name='Time [min]', null=True, blank=True)
    workout_plan = models.ForeignKey(
        WorkoutPlan, on_delete=models.CASCADE, unique_for_date=day,
        verbose_name='Add training to workout plan')
    accomplished = models.BooleanField(default=False)

    def training_info(self):
        """Prepare information about a training.

        :return: training info
        :rtype: str
        """
        info = [self.training_main]
        if self.distance_main:
            info.append(f'{self.distance_main}km')
        if self.time_main:
            info.append(f'{self.time_main}min')
        if self.training_additional:
            info.append(self.training_additional)
        if self.distance_additional:
            info.append(f'{self.distance_additional}km')
        if self.time_additional:
            info.append(f'{self.time_additional}min')
        return ' '.join(info)

    def __str__(self):
        """Return a string representation of the model."""
        return self.training_info()


class TrainingDiary(models.Model):
    """Stores a single entry in a training diary."""

    date = models.DateField(verbose_name="Date")
    training_info = models.CharField(max_length=128, verbose_name='Training')
    training_distance = models.DecimalField(
        max_digits=3, decimal_places=1, verbose_name='Total distance')
    training_time = models.SmallIntegerField(verbose_name='Total time')
    comments = models.CharField(
        max_length=256, verbose_name='Comments', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
