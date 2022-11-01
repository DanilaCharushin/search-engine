from django.urls import re_path

from .views import ping_view

urlpatterns = [
    re_path(r"^ping/?$", view=ping_view, name="dramatiq-ping"),
]
