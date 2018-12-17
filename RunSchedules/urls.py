"""RunSchedules URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from RunScheduleApp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    # url(r'^check_user/', get_user),
    # url(r'^workout/', WorkoutCalendar.as_view()),
    url(r'^workout_plan_add/', WorkoutPlanAdd.as_view()),
    url(r'^current_workout_plan/', CurrentWorkoutPlanView.as_view()),
    url(r'^workout_plan/(?P<id>\d+)$', WorkoutPlanView.as_view()),
]
