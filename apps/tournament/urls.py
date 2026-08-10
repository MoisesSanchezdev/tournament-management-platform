from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import (
    control_dashboard,
    control_division,
    control_division_stage,
    control_phase_detail,
    overview,
    participant_modal_detail,
)


app_name = "tournament"

urlpatterns = [
    path("", overview, name="overview"),
    path(
        "control/login/",
        LoginView.as_view(template_name="tournament/internal_login.html"),
        name="control_login",
    ),
    path("control/logout/", LogoutView.as_view(), name="control_logout"),
    path("control/", control_dashboard, name="control_dashboard"),
    path("control/divisiones/<int:competition_id>/", control_division, name="control_division"),
    path(
        "control/divisiones/<int:competition_id>/fases/<str:stage_key>/",
        control_division_stage,
        name="control_division_stage",
    ),
    path(
        "control/divisiones/<int:competition_id>/participantes/<int:state_id>/",
        participant_modal_detail,
        name="participant_modal_detail",
    ),
    path("control/fases/<int:phase_id>/", control_phase_detail, name="control_phase_detail"),
]
