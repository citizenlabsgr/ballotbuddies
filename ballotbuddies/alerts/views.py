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
        voter = user.voter
        profile = voter.profile

    newbie = Voter(user=User(pk=0))
    friend = Voter(user=User(first_name="Firstname", last_name="Lastname"))
    message = Message(profile=profile)
    message.add(friend, save=False)
    message.add(voter, save=False)

    emails = [
        helpers.get_login_email(newbie.user),
        helpers.get_login_email(user),
        helpers.get_invite_email(newbie.user, friend),
        helpers.get_invite_email(user, friend),
        helpers.get_activity_email(newbie.user, profile=profile, message=message),
        helpers.get_activity_email(user, message=message),
        helpers.get_voted_email(user),
    ]
    context = {"profile": profile, "emails": emails}

    return render(request, "debug/emails.html", context)
