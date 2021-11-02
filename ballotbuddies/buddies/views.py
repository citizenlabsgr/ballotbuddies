from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as force_login
from django.contrib.auth import logout as force_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from ballotbuddies.core.helpers import allow_debug, send_login_email

from .forms import FriendsForm, LoginForm, VoterForm
from .helpers import generate_sample_voters
from .models import Voter


def index(request):
    if referrer := request.GET.get("referrer"):
        request.session["referrer"] = referrer

    if request.user.is_authenticated and not referrer:
        return redirect("buddies:friends")

    context = {
        "community": sorted(generate_sample_voters(referrer)),
        "referrer": referrer,
    }
    return render(request, "friends/index.html", context)


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            voter: Voter = Voter.objects.from_email(
                form.cleaned_data["email"],
                request.session.get("referrer"),
            )

            if "debug" in request.POST and allow_debug(request):
                force_login(
                    request, voter.user, backend=settings.AUTHENTICATION_BACKENDS[0]
                )
                return redirect("buddies:friends")

            send_login_email(voter.user)
            domain = voter.email.split("@")[-1]
            return render(request, "login.html", {"domain": domain})
    else:
        form = LoginForm()

    context = {"form": form, "allow_debug": allow_debug(request)}
    return render(request, "login.html", context)


def logout(request):
    force_logout(request)
    return redirect("buddies:index")


@login_required
def profile(request):
    voter: Voter = Voter.objects.from_user(request.user)

    if not voter.complete:
        messages.info(request, "Please finish setting up your profile to continue.")
        return redirect("buddies:setup")

    _updated, error = voter.update_status()
    voter.save()
    if error:
        messages.error(request, error)

    form = VoterForm(initial=voter.data, locked=True)

    context = {"voter": voter, "form": form}
    return render(request, "profile/detail.html", context)


@login_required
def setup(request):
    voter: Voter = Voter.objects.from_user(request.user)
    if request.method == "POST":
        form = VoterForm(request.POST, instance=voter, initial=voter.data)
        if form.is_valid():
            voter = form.save()
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
def friends(request):
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
            messages.success(request, f"Successfully added {len(voters)} friend(s).")
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
def status(request, slug: str):
    voter: Voter = Voter.objects.get(slug=slug)

    if "ignore" in request.POST:
        request.user.voter.neighbors.remove(voter)
        request.user.voter.strangers.add(voter)
        request.user.voter.save()
        return HttpResponse()

    if "add" in request.POST:
        request.user.voter.neighbors.remove(voter)
        request.user.voter.friends.add(voter)
        request.user.voter.save()

    if "voted" in request.POST:
        voter.voted = timezone.now()
        voter.save()
        context = {"voter": voter}
        return render(request, "profile/_status.html", context)

    voter.update_status()
    voter.save()

    context = {"voter": voter}
    return render(request, "friends/_voter.html", context)
