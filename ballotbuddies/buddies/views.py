from django.contrib import messages
from django.contrib.auth import login as do_login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

import log

from ballotbuddies.core.helpers import allow_debug

from .forms import FriendsForm, LoginForm, VoterForm
from .models import User, Voter


def index(_request):
    return redirect("buddies:friends")


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():

            if "debug" in request.POST and allow_debug(request):
                user, created = User.objects.get_or_create(
                    email=form.cleaned_data["email"],
                    defaults=dict(username=form.cleaned_data["email"]),
                )
                if created:
                    log.info(f"Created user: {user}")
                do_login(request, user)
                return redirect("buddies:friends")

            # TODO: Send sesame login emails when not debugging
    else:
        form = LoginForm()
    context = {"form": form, "allow_debug": allow_debug(request)}
    return render(request, "login.html", context)


def logout(request):
    do_logout(request)
    return redirect("buddies:index")


@login_required
def profile(request):
    voter: Voter = Voter.objects.from_user(request.user)

    if not voter.complete:
        messages.info(request, "Please finish setting up your profile to continue.")
        return redirect("buddies:setup")

    voter.update()
    voter.save()

    context = {"voter": voter}
    return render(request, "profile/detail.html", context)


@login_required
def setup(request):
    voter: Voter = Voter.objects.from_user(request.user)
    if request.method == "POST":
        form = VoterForm(request.POST, instance=voter)
        if form.is_valid():
            voter = form.save()
            voter.user.first_name = form.cleaned_data["first_name"]
            voter.user.last_name = form.cleaned_data["last_name"]
            if voter.user.username != "admin":  # preserve default localhost user
                voter.user.username = str(voter)
            voter.user.save()
            messages.success(request, "Successfully updated your profile information.")
            return redirect("buddies:profile")
    else:
        form = VoterForm(instance=voter, initial=voter.data)
    context = {"voter": voter, "form": form}
    return render(request, "profile/setup.html", context)


@login_required
def friends(request):
    voter: Voter = Voter.objects.from_user(request.user)

    if not voter.complete:
        messages.info(request, "Please finish setting up your profile to continue.")
        return redirect("buddies:setup")

    if request.method == "POST":
        form = FriendsForm(request.POST)
        if form.is_valid():
            debug = "debug" in request.POST and allow_debug(request)
            Voter.objects.invite(voter, form.cleaned_data["emails"], send=not debug)
            return redirect("buddies:friends")
    else:
        form = FriendsForm()

    context = {
        "voter": voter,
        "friends": voter.friends.all(),
        "form": form,
        "allow_debug": allow_debug(request),
    }
    return render(request, "friends/index.html", context)


@login_required
def status(request, username: str):
    voter: Voter = Voter.objects.get(user__username=username)
    voter.update()
    voter.save()
    context = {"voter": voter}
    return render(request, "friends/_voter.html", context)
