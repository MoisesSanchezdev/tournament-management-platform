from django.urls import path

from .views import attendance_confirmation, registration_choice, registration_success, school_register, university_register


app_name = "participants"

urlpatterns = [
    path("", registration_choice, name="team_register"),
    path("colegios/", school_register, name="school_register"),
    path("universidades/", university_register, name="university_register"),
    path("exito/<str:registration_type>/", registration_success, name="registration_success"),
    path("confirmar-asistencia/<uuid:token>/", attendance_confirmation, name="attendance_confirmation"),
]
