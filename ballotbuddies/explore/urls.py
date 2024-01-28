from django.urls import path

from . import views

app_name = "explore"

urlpatterns = [
    path("", views.index, name="index"),  # type: ignore[arg-type]
    # Proposals
    path("proposals/", views.proposals_list, name="proposals"),  # type: ignore[arg-type]
    path("proposals/election/<int:election_id>/", views.proposals_by_election, name="proposals-election"),  # type: ignore[arg-type]
    path("proposals/district/<int:district_id>/", views.proposals_by_district, name="proposals-district"),  # type: ignore[arg-type]
    path("proposals/election/<int:election_id>/district/<district_id>/", views.proposals_by_election_and_district, name="proposals-election-district"),  # type: ignore[arg-type]
    # Positions
    path("positions/", views.positions_list, name="positions"),  # type: ignore[arg-type]
    path("positions/election/<int:election_id>/", views.positions_by_election, name="positions-election"),  # type: ignore[arg-type]
    path("positions/district/<int:district_id>/", views.positions_by_district, name="positions-district"),  # type: ignore[arg-type]
    path("positions/election/<int:election_id>/district/<district_id>/", views.positions_by_election_and_district, name="positions-election-district"),  # type: ignore[arg-type]
    # Elections
    path("elections/", views.elections_list, name="elections"),  # type: ignore[arg-type]
]
