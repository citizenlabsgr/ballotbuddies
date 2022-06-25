from django.contrib.auth.models import User
from django.core.mail import EmailMessage

import log
from sesame.utils import get_query_string

from ballotbuddies.core.helpers import build_url

from .models import Message, Profile


def get_login_email(user: User, path: str):
    url = build_url(path) + get_query_string(user)
    return EmailMessage(
        "Welcome to Michigan Ballot Buddies",
        f"Click this link to log in: {url}",
        "no-reply@michiganelections.io",
        [user.email],
    )


def send_login_email(user: User, path: str = "/"):
    profile: Profile = user.voter.profile
    if message := get_login_email(user, path):
        if user.email.endswith("@example.com"):
            log.warn(f"Skipped email for test user: {user}")
        elif message.send(fail_silently=False):
            profile.mark_alerted()


def get_invite_email(user: User, friend: User, path: str, *, extra: str = ""):
    url = build_url(path) + get_query_string(user)
    name = friend.display_name  # type: ignore
    return EmailMessage(
        f"Join {name} on Michigan Ballot Buddies{extra}",
        "Your friend has challenged you to vote in every election. Let's keep each other accountable!"
        "\n\n"
        f"Click this link to view your profile: {url}",
        "no-reply@michiganelections.io",
        [user.email],
    )


# TODO: hard-code path?
def send_invite_email(user: User, friend: User, path: str = "/profile", *, debug=False):
    profile: Profile = user.voter.profile
    extra = " [debug]" if debug else ""
    if message := get_invite_email(user, friend, path, extra=extra):
        if user.email.endswith("@example.com"):
            log.warn(f"Skipped email for test user: {user}")
        elif message.send(fail_silently=False):
            profile.mark_alerted()


def get_activity_email(user: User):
    profile: Profile = user.voter.profile
    message: Message = Message.objects.get_draft(profile)
    url = build_url("/profile") + get_query_string(user)
    return EmailMessage(
        message.subject,
        message.body + "\n\n" + f"Click this link to view your progress: {url}",
        "no-reply@michiganelections.io",
        [user.email],
    )


def send_activity_email(user: User):
    if email := get_activity_email(user):
        if user.email.endswith("@example.com"):
            log.warn(f"Skipped email for test user: {user}")
        elif email.send(fail_silently=False):
            # TODO: mark sent
            # message.mark_sent()
            pass
