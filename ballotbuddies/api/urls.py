from django.urls import include, path

from . import views

urlpatterns = [
    path("provision-voter/", views.provision_voter),
    path("update-ballot/", views.update_ballot),
    path("client/", include("rest_framework.urls")),
]
