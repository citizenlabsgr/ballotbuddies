from datetime import timedelta

from django.contrib.auth.models import User
from django.core.mail import EmailMessage

import log
from sesame.utils import get_query_string

from ballotbuddies.core.helpers import build_url

from .models import Message, Profile


def update_profiles():
    query = Profile.objects.filter(staleness__lte=timedelta(days=0))
    log.info(f"Updating {query.count()} profiles(s)")
    profile: Profile
    for profile in query:
        profile.save()


def get_login_email(user: User):
    url = build_url("/") + get_query_string(user)
    return EmailMessage(
        "Welcome to Michigan Ballot Buddies",
        f"Click this link to log in: {url}",
        "no-reply@michiganelections.io",
        [user.email],
    )


def send_login_email(user: User):
    if message := get_login_email(user):
        if user.email.endswith("@example.com"):
            log.warn(f"Skipped login email for test user: {user}")
        elif message.send(fail_silently=False):
            log.info(f"Sent login email: {user}")


def get_invite_email(user: User, friend: User, *, extra: str = ""):
    url = build_url("/about") + get_query_string(user)
    name = friend.display_name  # type: ignore
    return EmailMessage(
        f"Join {name} on Michigan Ballot Buddies{extra}",
        "Your friend has challenged you to vote in every election. Let's keep each other accountable!"
        "\n\n"
        f"Click this link to get started: {url}",
        "no-reply@michiganelections.io",
        [user.email],
    )


def send_invite_email(user: User, friend: User, *, debug=False):
    extra = " [debug]" if debug else ""
    if message := get_invite_email(user, friend, extra=extra):
        if user.email.endswith("@example.com"):
            log.warn(f"Skipped invite email for test user: {user}")
        elif message.send(fail_silently=False):
            log.info(f"Sent invite email: {user}")


def get_activity_email(user: User, message: Message | None = None):
    profile: Profile = user.voter.profile
    message = message or Message.objects.get_draft(profile)
    url = build_url("/about") + get_query_string(user)
    return EmailMessage(
        message.subject,
        message.body + "\n\n" + f"Click this link to view your progress: {url}",
        "no-reply@michiganelections.io",
        [user.email],
    )


def send_activity_email(user: User):
    profile: Profile = user.voter.profile
    if email := get_activity_email(user):
        if user.email.endswith("@example.com"):
            log.warn(f"Skipped activity email for test user: {user}")
        elif email.send(fail_silently=False):
            log.info(f"Sent activity email: {user}")
            message: Message = Message.objects.get_draft(profile)
            message.mark_sent()
            profile.mark_alerted()
