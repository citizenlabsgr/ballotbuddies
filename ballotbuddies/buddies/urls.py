from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("profile/", views.profile, name="profile"),
    path("profile/setup/", views.setup, name="setup"),
    path("friends/", views.friends, name="friends"),
    path("friends/<slug>", views.friends_profile, name="friends-profile"),
    path("friends/<slug>/setup/", views.friends_setup, name="friends-setup"),
    path("friends/<slug>/_status", views.status, name="status"),
    path("invite/", views.invite, name="invite"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
]

app_name = "buddies"
