from django.urls import include, path, re_path
from drf_spectacular import views

from app.apps.api.v1.views.ranks import calculate_ranks
from app.apps.api.v1.views.search import search_by_query

urlpatterns = [
    re_path(r"^schema/?$", views.SpectacularAPIView.as_view(), name="schema"),
    re_path(r"^swagger/?$", views.SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    re_path(r"^redoc/?$", views.SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("v1/", include("app.apps.api.v1.urls")),
    path("search", search_by_query, name="search-by-query"),
    path("ranks", calculate_ranks, name="calculate-ranks"),
]
