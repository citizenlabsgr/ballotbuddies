from django.urls import path

from . import views

app_name = "explore"

urlpatterns = [
    path("", views.index, name="index"),  # type: ignore[arg-type]
    path("elections/<int:election_id>/", views.election_items, name="election"),  # type: ignore[arg-type]
]
