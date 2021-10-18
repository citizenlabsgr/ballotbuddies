from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail

from sesame.utils import get_query_string


def build_url(path: str) -> str:
    assert settings.BASE_URL
    assert path.startswith("/")
    return settings.BASE_URL + path


def allow_debug(request) -> bool:
    if not settings.ALLOW_DEBUG:
        return False
    if request.GET.get("debug") == "false":
        return False
    if request.GET.get("debug"):
        return True
    return settings.DEBUG


def send_login_email(user: User, path: str = "/"):
    url = build_url(path) + get_query_string(user)
    send_mail(
        "Welcome to Ballot Buddies",
        f"Please click this link to log in: {url}",
        "no-reply@michiganelections.io",
        [user.email],
        fail_silently=False,
    )


def send_invite_email(user: User, friend: User, path: str = "/profile"):
    url = build_url(path) + get_query_string(user)
    name = friend.get_full_name()
    send_mail(
        f"Join {name} on Ballot Buddies",
        "Your friend has challenged you to vote in every election!"
        "\n\n"
        f"Please click this link to view your profile: {url}",
        "no-reply@michiganelections.io",
        [user.email],
        fail_silently=False,
    )
