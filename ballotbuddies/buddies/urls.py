from django.urls import path

from . import views

app_name = "buddies"

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("profile/setup/", views.setup, name="setup"),
    path("profile/unsubscribe/", views.unsubscribe, name="unsubscribe"),
    path("profile/delete/", views.delete, name="delete"),
    path("friends/", views.friends, name="friends"),
    path("friends/search/", views.friends_search, name="search"),
    path("friends/invite/", views.invite, name="invite"),
    path("friends/<slug>", views.friends_profile, name="friends-profile"),
    path("friends/<slug>/setup/", views.friends_setup, name="friends-setup"),
    path("friends/<slug>/_status", views.status, name="status"),
    path("friends/<slug>/_email", views.friends_email, name="email"),
]
