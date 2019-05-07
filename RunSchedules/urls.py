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
from django.urls import path, include

from RunScheduleApp.views import *

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    url(r'^$', MainPageView.as_view()),
    url(r'^workout/(?P<month_number_requested>\d+)$', WorkoutPlanView.as_view()),
    url(r'^workout_list$', WorkoutsList.as_view()),
    url(r'^workout_plan_add', WorkoutPlanAdd.as_view(), name='workout_plan_add'),
    url(r'^workout_plan_edit/(?P<plan_id>\d+)$', WorkoutPlanEdit.as_view(), name='workout_plan_edit'),
    url(r'^plan_details/(?P<plan_id>\d+)$', PlanDetailsView.as_view()),
    url(r'^training_add/(?P<plan_id>\d+)/(?P<month_number>\d+)$', TrainingAdd.as_view()),
    url(r'^training_add/(?P<plan_id>\d+)/(?P<month_number>\d+)/(?P<date>.+)$', TrainingAdd.as_view()),
    url(r'^training_delete/(?P<training_id>\d+)$', TrainingDelete.as_view()),
    url(r'^training_edit/(?P<plan_id>\d+)/(?P<month_number>\d+)/(?P<training_id>\d+)$', TrainingEdit.as_view()),
    url(r'^login$', LoginView.as_view()),
    url(r'^logout$', LogoutView.as_view()),
    url(r'^registration$', RegistrationView.as_view()),
    url(r'^profile$', UserProfileView.as_view()),
    url(r'^edit_profile$', EditUserView.as_view()),
    url(r'^password_change$', PasswordChangeView.as_view()),
    url(r'^select_active_plan$', SelectActivePlanView.as_view()),
]
