from django.urls import path

from . import views

app_name = "buddies"

urlpatterns = [
    # Profile
    path("profile/", views.profile, name="profile"),
    path("profile/setup/", views.profile_setup, name="setup"),
    path("profile/unsubscribe/", views.profile_unsubscribe, name="unsubscribe"),
    path("profile/delete/", views.profile_delete, name="delete"),
    # Friends
    path("friends/", views.friends, name="friends"),
    path("friends/search/", views.friends_search, name="search"),
    path("friends/invite/", views.friends_invite, name="invite"),
    path("friends/<slug>", views.friends_profile, name="friends-profile"),
    path("friends/<slug>/setup/", views.friends_setup, name="friends-setup"),
    path("friends/<slug>/_status", views.friends_status, name="status"),
    path("friends/<slug>/_email", views.friends_email, name="email"),
    # Notes
    path("friends/<slug>/_note/", views.friends_note, name="note"),
]
