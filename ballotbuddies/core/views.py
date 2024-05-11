from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as force_login
from django.contrib.auth import logout as force_logout
from django.http import HttpRequest
from django.shortcuts import redirect, render

import log

from ballotbuddies.alerts.helpers import send_login_email
from ballotbuddies.buddies.helpers import generate_sample_voters
from ballotbuddies.buddies.models import Voter

from .forms import LoginForm, SignupForm
from .helpers import allow_debug, parse_domain


def index(request: HttpRequest):
    if referrer := request.GET.get("referrer", ""):
        log.info(f"Referrer: {referrer}")
        request.session["referrer"] = referrer

    if request.user.is_authenticated:
        if not referrer:
            return redirect("buddies:friends")

        friend, added = request.user.voter.add_friend(referrer)
        if added:
            messages.success(request, "Successfully added 1 friend.")
        if friend:
            return redirect("buddies:friends")

    context = {
        "preview": True,
        "community": sorted(generate_sample_voters(referrer)),
    }
    return render(request, "friends/index.html", context)


def join(request: HttpRequest):
    referrer = request.session.get("referrer", "")
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                voter = Voter.objects.from_email(email, referrer, create=False)
            except Voter.DoesNotExist:
                voter = Voter.objects.from_email(email, referrer)
                voter.birth_date = form.cleaned_data["birth_date"]
                voter.zip_code = form.cleaned_data["zip_code"]
                voter.save()
                voter.user.update_name(  # type: ignore
                    request,
                    form.cleaned_data["first_name"],
                    form.cleaned_data["last_name"],
                )
                log.info(f"Updated voter: {voter}")
            else:
                log.info(f"Voter already exists: {voter}")
                request.method = "POST"
                request.POST = {"email": email}  # type: ignore
                messages.info(
                    request,
                    "It looks like you already have an account. Check your email for a login link.",
                )
                return login(request)

            messages.success(request, "Successfully created your voter profile.")
            force_login(
                request, voter.user, backend=settings.AUTHENTICATION_BACKENDS[0]
            )
            send_login_email(voter.user)
            return redirect(request.GET.get("next") or "buddies:profile")
    else:
        form = SignupForm()

    context = {"form": form}
    return render(request, "signup.html", context)


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
                return redirect(request.GET.get("next") or "core:index")

            send_login_email(voter.user)
            domain, standard = parse_domain(voter.user.email)
            context = {
                "domain": domain,
                "standard": standard and request.user_agent.is_pc,  # type: ignore[attr-defined]
            }
            return render(request, "login.html", context)
    else:
        form = LoginForm()

    context = {
        "form": form,
        "debug": allow_debug(request),
    }
    return render(request, "login.html", context)


def logout(request: HttpRequest):
    force_logout(request)
    return redirect("core:index")


def about(request):
    return render(request, "about/index.html")


def zapier(request: HttpRequest):
    return render(request, "zapier.html")
