from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path

urlpatterns = [
    path("", include("django_prometheus.urls")),
    re_path(r"^ping/?$", view=lambda request: HttpResponse("pong"), name="ping"),
    path("admin/", admin.site.urls),
    path("dramatiq/", include("app.apps.dramatiq.urls")),
    path("api/", include("app.apps.api.urls")),
]
