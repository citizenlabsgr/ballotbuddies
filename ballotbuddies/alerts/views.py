from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ballotbuddies.buddies.models import Voter
from ballotbuddies.core.models import User

from . import helpers
from .models import Message


@login_required
def debug(request, slug=""):
    if slug:
        voter = Voter.objects.get(slug=slug)
        user = voter.user
        profile = voter.profile
    else:
        user = request.user
        profile = user.voter.profile

    friend = User(first_name="Firstname", last_name="Lastname")
    message: Message = Message.objects.get_draft(profile)
    message.activity[friend.id] = f"{friend.first_name} is doing stuff"

    emails = [
        helpers.get_login_email(user),
        helpers.get_invite_email(user, friend),
        helpers.get_activity_email(user, message),
    ]
    context = {"profile": profile, "emails": emails}

    return render(request, "debug/emails.html", context)
