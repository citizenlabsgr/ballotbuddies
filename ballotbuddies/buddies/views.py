import datetime

from django.contrib import messages
from django.contrib.auth import login as do_login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

import log

from .forms import LoginForm, VoterForm
from .models import User, Voter


def current_datetime(request):
    log.debug(request)
    now = datetime.datetime.now()
    html = f"<html><body>Welcome to ballotbuddies.<br>It is now {now}.</body></html>"
    return HttpResponse(html)


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            # TODO: Send sesame login emails when not debugging
            user, created = User.objects.get_or_create(
                email=form.cleaned_data["email"],
                defaults=dict(username=form.cleaned_data["email"]),
            )
            if created:
                log.info(f"Created user: {user}")
            do_login(request, user)
            return redirect("buddies:profile")
    else:
        form = LoginForm()
    context = {"form": form}
    return render(request, "login.html", context)


def logout(request):
    do_logout(request)
    return redirect("buddies:index")


@login_required
def profile(request):
    voter = Voter.objects.from_user(request.user)
    if not voter.complete:
        messages.info(request, "Please finish setting up your profile to continue.")
        return redirect("buddies:setup")
    context = {"voter": voter}
    return render(request, "profile/detail.html", context)


@login_required
def setup(request):
    voter = Voter.objects.from_user(request.user)
    if request.method == "POST":
        form = VoterForm(request.POST, instance=voter)
        if form.is_valid():
            voter = form.save()
            voter.user.first_name = form.cleaned_data["first_name"]
            voter.user.last_name = form.cleaned_data["last_name"]
            voter.user.username = f"{voter.user.get_full_name()} ({voter.user.email})"
            voter.user.save()
            messages.success(request, "Successfully updated your profile information.")
            return redirect("buddies:profile")
    else:
        form = VoterForm(instance=voter, initial=voter.data)
    context = {"voter": voter, "form": form}
    return render(request, "profile/setup.html", context)
