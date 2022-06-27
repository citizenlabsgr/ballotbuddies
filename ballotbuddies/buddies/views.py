from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as force_login
from django.contrib.auth import logout as force_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

import log

from ballotbuddies.alerts.helpers import send_login_email
from ballotbuddies.core.helpers import allow_debug

from .forms import FriendsForm, LoginForm, VoterForm
from .helpers import generate_sample_voters
from .models import Voter


def index(request: HttpRequest):
    if referrer := request.GET.get("referrer", ""):
        log.info(f"Referrer: {referrer}")
        request.session["referrer"] = referrer

    if request.user.is_authenticated and not referrer:
        return redirect("buddies:friends")

    context = {
        "community": sorted(generate_sample_voters(referrer)),
        "referrer": referrer,
    }
    return render(request, "friends/index.html", context)


def about(request):
    return render(request, "about/index.html")


def login(request: HttpRequest):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            voter: Voter = Voter.objects.from_email(
                form.cleaned_data["email"],
                request.session.get("referrer", ""),
            )

            if "debug" in request.POST and allow_debug(request):
                force_login(
                    request, voter.user, backend=settings.AUTHENTICATION_BACKENDS[0]
                )
                return redirect(request.GET.get("next") or "buddies:index")

            send_login_email(voter.user)
            domain = voter.email.split("@")[-1]
            return render(request, "login.html", {"domain": domain})
    else:
        form = LoginForm()

    context = {"form": form, "allow_debug": allow_debug(request)}
    return render(request, "login.html", context)


def logout(request: HttpRequest):
    force_logout(request)
    return redirect("buddies:index")


@login_required
def profile(request: HttpRequest):
    assert isinstance(request.user, User)
    voter: Voter = Voter.objects.from_user(request.user)

    if not voter.complete:
        messages.info(request, "Please finish setting up your profile to continue.")
        return redirect("buddies:setup")

    if request.method == "POST":
        if voter.profile.never_alert:
            message = "You will now receive periodic reminder emails."
            voter.profile.never_alert = False
        else:
            message = "You will no longer receive reminder emails."
            voter.profile.never_alert = True
        voter.profile.save()
        messages.info(request, message)
        return redirect("buddies:profile")

    if not voter.updated:
        _updated, error = voter.update_status()
        voter.save()
        if error:
            messages.error(request, error)

    form = VoterForm(initial=voter.data, locked=True)
    voter.profile.mark_viewed()  # type: ignore

    context = {"voter": voter, "form": form}
    return render(request, "profile/detail.html", context)


@login_required
def setup(request: HttpRequest):
    assert isinstance(request.user, User)
    voter: Voter = Voter.objects.from_user(request.user)

    if request.method == "POST":
        form = VoterForm(request.POST, instance=voter, initial=voter.data)
        if form.is_valid():
            voter = form.save()
            voter.updated = None
            voter.save()
            voter.user.update_name(  # type: ignore
                request, form.cleaned_data["first_name"], form.cleaned_data["last_name"]
            )
            messages.success(request, "Successfully updated your profile information.")
            return redirect("buddies:profile")
    else:
        form = VoterForm(instance=voter, initial=voter.data)

    context = {"voter": voter, "form": form}
    return render(request, "profile/setup.html", context)


@login_required
def friends(request: HttpRequest):
    assert isinstance(request.user, User)
    voter: Voter = Voter.objects.from_user(request.user)

    if not voter.complete:
        messages.info(request, "Please finish setting up your profile to continue.")
        return redirect("buddies:setup")

    if not voter.updated:
        voter.update_status()
        voter.save()

    if request.method == "POST":
        form = FriendsForm(request.POST)
        if form.is_valid():
            voters = Voter.objects.invite(voter, form.cleaned_data["emails"])
            s = "" if len(voters) == 1 else "s"
            messages.success(request, f"Successfully added {len(voters)} friend{s}.")
            return redirect("buddies:friends")
    else:
        form = FriendsForm()

    context = {
        "community": voter.community,
        "recommended": voter.neighbors.all(),
        "form": form,
        "allow_debug": allow_debug(request),
    }
    return render(request, "friends/index.html", context)


@login_required
def friends_profile(request: HttpRequest, slug: str):
    voter: Voter = Voter.objects.get(slug=slug)
    getattr(voter, "profile")  # ensure Profile exists
    if voter.user == request.user:
        return redirect("buddies:profile")

    form = VoterForm(initial=voter.data, locked=True)
    context = {"voter": voter, "form": form}
    return render(request, "friends/detail.html", context)


@login_required
def friends_setup(request: HttpRequest, slug: str):
    voter: Voter = Voter.objects.get(slug=slug)

    if request.method == "POST":
        form = VoterForm(request.POST, instance=voter, initial=voter.data)
        if form.is_valid():
            voter = form.save()
            voter.save()
            voter.user.update_name(  # type: ignore
                request, form.cleaned_data["first_name"], form.cleaned_data["last_name"]
            )
            messages.success(request, "Successfully updated your friend's information.")
            return redirect("buddies:friends-profile", slug=slug)
    else:
        form = VoterForm(instance=voter, initial=voter.data)

    context = {"voter": voter, "form": form}
    return render(request, "friends/setup.html", context)


@login_required
def status(request: HttpRequest, slug: str):
    assert isinstance(request.user, User)
    voter: Voter = Voter.objects.get(slug=slug)
    render_as_table = request.method == "GET"

    if "ignore" in request.POST:
        log.info(f"Unfollowing voter: {voter}")
        request.user.voter.friends.remove(voter)
        request.user.voter.neighbors.remove(voter)
        request.user.voter.strangers.add(voter)
        request.user.voter.save()
        return HttpResponse()

    if "add" in request.POST:
        log.info(f"Following voter: {voter}")
        request.user.voter.neighbors.remove(voter)
        request.user.voter.friends.add(voter)
        request.user.voter.save()

    if "absentee" in request.POST:
        log.info(f"Recording in-person intention: {voter}")
        assert request.POST["absentee"] == "false"
        voter.absentee = False
        render_as_table = True

    if "voted" in request.POST:
        log.info(f"Recording vote: {voter}")
        voter.voted = timezone.now()
        render_as_table = True

    if "reset" in request.POST:
        log.info(f"Clearing vote: {voter}")
        voter.reset_status()
        render_as_table = True

    voter.update_status()
    voter.save()
    context = {"voter": voter, "recommended": []}

    if render_as_table:
        return render(request, "profile/_table.html", context)

    return render(request, "friends/_row.html", context)


@login_required
def invite(request: HttpRequest):
    assert isinstance(request.user, User)
    voter: Voter = Voter.objects.from_user(request.user)

    if request.method == "POST":
        form = FriendsForm(request.POST)
        if form.is_valid():
            voters = Voter.objects.invite(voter, form.cleaned_data["emails"])
            s = "" if len(voters) == 1 else "s"
            messages.success(request, f"Successfully added {len(voters)} friend{s}.")
            return redirect("buddies:friends")
    else:
        form = FriendsForm()

    context = {"form": form}
    return render(request, "invite/index.html", context)
