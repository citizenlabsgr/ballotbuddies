from django.urls import include, path

from . import views

urlpatterns = [
    path("update-ballot/", views.update_ballot),
    path("client/", include("rest_framework.urls")),
]
