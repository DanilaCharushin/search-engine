from django.urls import include, path, re_path
from drf_spectacular import views

urlpatterns = [
    re_path(r"^schema/?$", views.SpectacularAPIView.as_view(), name="schema"),
    re_path(r"^swagger/?$", views.SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    re_path(r"^redoc/?$", views.SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("v1/", include("app.apps.api.v1.urls")),
]
