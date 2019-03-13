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
    url(r'^$', MainPageView.as_view()),
    url(r'^workout/(?P<month_number_requested>\d+)$', CurrentWorkoutPlanView.as_view()),
    url(r'^workout_list$', WorkoutsList.as_view()),
    url(r'^workout_plan_add/', WorkoutPlanAdd.as_view()),
    url(r'^workout_plan_edit/(?P<plan_id>\d+)$', WorkoutPlanEdit.as_view()),
    # url(r'^current_workout_plan/', CurrentWorkoutPlanView.as_view()),
    url(r'^plan_details/(?P<id>\d+)$', PlanDetailsView.as_view()),
    url(r'^daily_training_add/(?P<id>\d+)$', DailyTrainingAdd.as_view()),
    url(r'^daily_training_add/(?P<id>\d+)/(?P<date>.+)$', DailyTrainingAdd.as_view()),
    url(r'^daily_training_delete/(?P<id>\d+)$', DailyTrainingDelete.as_view()),
    url(r'^daily_training_edit/(?P<plan_id>\d+)/(?P<id>\d+)$', DailyTrainingEdit.as_view()),
    url(r'^login$', LoginView.as_view()),
    url(r'^logout$', LogoutView.as_view()),
    url(r'^registration$', RegistrationView.as_view()),
    url(r'^profile$', UserProfileView.as_view()),
    url(r'^edit_profile$', EditUserView.as_view()),
    url(r'^password_change$', PasswordChangeView.as_view()),
    url(r'^select_active_plan$', SelectActivePlanView.as_view()),
]
