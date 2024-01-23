from django.urls import path

from . import views

app_name = "explore"

urlpatterns = [
    path("", views.index, name="index"),  # type: ignore[arg-type]
    path("election/<int:election_id>/", views.by_election, name="election"),  # type: ignore[arg-type]
    path("district/<int:district_id>/", views.by_district, name="district"),  # type: ignore[arg-type]
]
