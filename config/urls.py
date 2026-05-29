from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("registro/", include("apps.participants.urls")),
    path("torneo/", include("apps.tournament.urls")),
]
