from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("join/", views.join, name="join"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
]
