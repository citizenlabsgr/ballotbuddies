from django.contrib.auth.models import User
from django.core.mail import send_mail

import log
from sesame.utils import get_query_string

from ballotbuddies.core.helpers import build_url


def send_login_email(user: User, path: str = "/"):
    if user.email.endswith("@example.com"):
        log.warn(f"Skipped email for test user: {user}")
        return
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
    name = friend.display_name  # type: ignore
    send_mail(
        f"Join {name} on Ballot Buddies",
        "Your friend has challenged you to vote in every election!"
        "\n\n"
        f"Please click this link to view your profile: {url}",
        "no-reply@michiganelections.io",
        [user.email],
        fail_silently=False,
    )
