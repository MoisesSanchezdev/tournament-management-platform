from django.urls import path

from . import views


app_name = "invitations"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("plantillas/", views.template_list, name="template_list"),
    path("plantillas/nueva/", views.template_create, name="template_create"),
    path("plantillas/<int:template_id>/previsualizar/", views.template_preview, name="template_preview"),
    path("invitaciones/", views.invitations, name="invitations"),
    path("confirmaciones/", views.confirmations, name="confirmations"),
    path("historial/", views.history, name="history"),
]
