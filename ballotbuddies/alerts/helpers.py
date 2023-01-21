# TODO: Upgrade mypy to 0.991+ when django-stubs supports it
# mypy: ignore_errors

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

import log
from sesame.utils import get_query_string

from ballotbuddies.core.helpers import build_url

from .models import Message, Profile

if TYPE_CHECKING:
    from ballotbuddies.buddies.models import Voter


def update_profiles():
    age = timezone.now() - timedelta(days=1, hours=1)
    query = Profile.objects.filter(updated_at__lte=age)
    log.info(f"Updating {query.count()} profiles(s)")
    profile: Profile
    for profile in query:
        profile.save()


def get_login_email(user: User):
    subject = "Welcome to Michigan Ballot Buddies"
    context = {
        "name": user.voter.nickname or user.first_name or "Voter",
        "complete": user.voter.complete,
        "url": build_url("/about"),
        "query_string": get_query_string(user),
    }
    body = render_to_string("emails/login.html", context)
    email = EmailMessage(subject, body, settings.EMAIL, [user.email])
    email.content_subtype = "html"
    return email


def send_login_email(user: User):
    if message := get_login_email(user):
        if user.email.endswith("@example.com"):
            log.warn(f"Skipped login email for test user: {user}")
        elif message.send(fail_silently=False):
            log.info(f"Sent login email: {user}")


def get_invite_email(user: User, friend: Voter, *, extra: str = ""):
    subject = f"Join {friend.display_name} on Michigan Ballot Buddies{extra}"
    context = {
        "name": user.voter.nickname or user.first_name or "Voter",
        "complete": user.voter.complete,
        "friend": friend,
        "url": build_url("/about"),
        "query_string": get_query_string(user),
    }
    body = render_to_string("emails/invite.html", context)
    email = EmailMessage(subject, body, settings.EMAIL, [user.email])
    email.content_subtype = "html"
    return email


def send_invite_email(user: User, friend: Voter, *, debug=False):
    extra = " [debug]" if debug else ""
    if message := get_invite_email(user, friend, extra=extra):
        if user.email.endswith("@example.com"):
            log.warn(f"Skipped invite email for test user: {user}")
        elif message.send(fail_silently=False):
            log.info(f"Sent invite email: {user}")


def get_activity_email(user: User, message: Message | None = None):
    profile: Profile = user.voter.profile
    message = message or profile.message
    context = {
        # TODO: Move this to property
        "name": user.voter.nickname or user.first_name or "Voter",
        "complete": user.voter.complete,
        "message": message,
        "url": build_url("/about"),
        "query_string": get_query_string(user),
    }
    body = render_to_string("emails/activity.html", context)
    email = EmailMessage(message.subject, body, settings.EMAIL, [user.email])
    email.content_subtype = "html"
    return email


def send_activity_email(user: User):
    profile: Profile = user.voter.profile
    if email := get_activity_email(user):
        if user.email.endswith("@example.com"):
            log.warn(f"Skipped activity email for test user: {user}")
        elif email.send(fail_silently=False):
            log.info(f"Sent activity email: {user}")
            profile.mark_alerted()


def send_activity_emails(day: str) -> int:
    if day and timezone.now().strftime("%A") != day:
        log.warn(f"Emails are only sent on {day}")
        return 0

    count = 0
    for profile in Profile.objects.filter(will_alert=True):
        send_activity_email(profile.voter.user)
        count += 1
    return count
