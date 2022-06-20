from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("profile/", views.profile, name="profile"),
    path("profile/setup/", views.setup, name="setup"),
    path("friends/", views.friends, name="friends"),
    path("friends/<slug>", views.friend, name="friend"),
    path("friends/<slug>/_status", views.status, name="status"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
]

app_name = "buddies"
