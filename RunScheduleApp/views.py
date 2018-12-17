from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from datetime import datetime
from calendar import HTMLCalendar
from RunScheduleApp.forms import *


# Create your views here.


def get_user(request):
    current_user = request.user
    return current_user


class WorkoutPlanAdd(View):  # zapytaj o poprawność tego i czy dodać warunek na AnnonymusUser
    def get(self, request):
        form = WorkoutPlanForm()
        return render(request, 'RunScheduleApp/workout_plan_add.html', {'form': form})

    def post(self, request):
        new_workout_plan = WorkoutPlan()
        form = WorkoutPlanForm(request.POST, instance=new_workout_plan)
        if form.is_valid():
            form.instance.owner = get_user(request)
            # if form.instance.is_active == True:
            #     pass TODO(napisać funkcję deaktywującą inne plany)
            form.save()
            return HttpResponse('Dodano plan')
        return render(request, 'RunScheduleApp/workout_plan_add.html', {'form': form})


class CurrentWorkoutPlanView(View):
    def get(self, request):
        logged_user = get_user(request)
        if logged_user.is_anonymous == True:
            return redirect('/login')
        workout_plan = WorkoutPlan.objects.filter(owner=get_user(request)).filter(is_active=True)
        return render(request, "RunScheduleApp/current_workout_plan_view.html", {'workout_plan': workout_plan})


class WorkoutPlanView(View):
    def get(self, request, id):
        workout_plan = WorkoutPlan.objects.get(pk=id)
        return render(request, "RunScheduleApp/workout_plan.html", {'workout_plan': workout_plan})



# class WorkoutCalendar(View):
#     def get(self, request):
#         date_now = datetime.now().date()
#         cal = CalendarTest().formatmonth(date_now.year, date_now.month)
#         return HttpResponse(cal)
#
#
# class CalendarTest(HTMLCalendar):
#
#     def formatday(self, day, weekday):
#         """
#         Return a day as a table cell.
#         """
#         date_now = datetime.now().date()
#         if day == date_now.day:
#             return '<td bgcolor= "green" class="%s">%d</td>' % (self.cssclasses[weekday], day)
#         elif day == 0:
#             return '<td class="noday">&nbsp;</td>'  # day outside month
#         else:
#             return '<td class="%s"><a href="%s">%d</a></td>' % (self.cssclasses[weekday], day, day)
