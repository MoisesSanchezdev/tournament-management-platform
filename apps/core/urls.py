from django.urls import path

from .views import home, rules_page, sponsors_page


app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("reglas/", rules_page, name="rules"),
    path("patrocinadores/", sponsors_page, name="sponsors"),
]
