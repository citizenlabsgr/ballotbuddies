from django.shortcuts import render

from ballotbuddies.core.models import User

from . import helpers


def debug(request):
    friend = User(first_name="Firstname", last_name="Lastname")
    emails = [
        helpers.get_login_email(request.user, "/test-login"),
        helpers.get_invite_email(request.user, friend, "/test-invite"),
    ]
    context = {"profile": request.user.voter.profile, "emails": emails}
    return render(request, "debug/emails.html", context)
