from django.urls import path

from . import views

urlpatterns = [
    path("", views.current_datetime, name="index"),
    path("profile/", views.profile, name="profile"),
    path("profile/setup/", views.setup, name="setup"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
]

app_name = "buddies"
