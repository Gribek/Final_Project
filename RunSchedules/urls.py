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
    url(r'^$', MainPageView.as_view(), name='home_page'),
    path('workout/<int:month>/<int:year>',
        WorkoutPlanView.as_view(), name='current_workout'),
    url(r'^workout_list$', WorkoutsList.as_view(), name='workout_plans'),
    url(r'^workout_plan_add', WorkoutPlanAdd.as_view(),
        name='workout_plan_add'),
    url(r'^workout_plan_edit/(?P<plan_id>\d+)$', WorkoutPlanEdit.as_view(),
        name='workout_plan_edit'),
    url(r'^plan_details/(?P<plan_id>\d+)$', PlanDetailsView.as_view(),
        name='plan_details'),
    path('training_add/<int:plan_id>', TrainingAdd.as_view(),
         name='add_training'),
    path('training_add/<int:plan_id>/<int:month>/<int:year>',
         TrainingAdd.as_view(), name='add_training_month'),
    path('training_add/<int:plan_id>/<int:month>/<int:year>/<training_date>',
         TrainingAdd.as_view(), name='add_training_date'),
    url(r'^training_delete/(?P<training_id>\d+)$', TrainingDelete.as_view(),
        name='delete_training'),
    path('training_edit/<int:plan_id>/<int:training_id>',
         TrainingEdit.as_view(), name='edit_training'),
    path('training_edit/<int:plan_id>/<int:training_id>/<int:month>/<int:year>',
         TrainingEdit.as_view(), name='edit_training_month'),
    url(r'^login$', LoginView.as_view(), name='login'),
    url(r'^logout$', LogoutView.as_view(), name='logout'),
    url(r'^registration$', RegistrationView.as_view(), name='registration'),
    url(r'^profile$', UserProfileView.as_view(), name='profile'),
    url(r'^edit_profile$', EditUserView.as_view(), name='edit_profile'),
    url(r'^password_change$', PasswordChangeView.as_view(),
        name='change_password'),
    url(r'^select_active_plan$', SelectActivePlanView.as_view(),
        name='select_active_plan'),
    url(r'^training_diary_entry_add/(?P<training_id>\d+)$',
        TrainingDiaryEntryAdd.as_view(), name='diary_entry_add'),
    url(r'^training_diary$', TrainingDiaryView.as_view(),
        name='training_diary'),
]
