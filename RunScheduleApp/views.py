from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from datetime import datetime
from calendar import HTMLCalendar
from RunScheduleApp.forms import *


# Create your views here.


def get_user(request):
    current_user = request.user
    return current_user


class WorkoutPlanView(View):  # zapytaj o poprawność tego i czy dodać warunek na AnnonymusUser
    def get(self, request):
        form = WorkoutPlanForm()
        return render(request, 'RunScheduleApp/workout_plan_add.html', {'form': form})

    def post(self, request):
        new_workout_plan = WorkoutPlan()
        form = WorkoutPlanForm(request.POST, instance=new_workout_plan)
        if form.is_valid():
            form.instance.owner = get_user(request)
            form.save()
            return HttpResponse('Dodano plan')

