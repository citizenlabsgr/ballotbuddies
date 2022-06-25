from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ballotbuddies.buddies.models import Voter
from ballotbuddies.core.models import User

from . import helpers


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
    emails = [
        helpers.get_login_email(user, "/test-login"),
        helpers.get_invite_email(user, friend, "/test-invite"),
    ]
    context = {"profile": profile, "emails": emails}

    return render(request, "debug/emails.html", context)
