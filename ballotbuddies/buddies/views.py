from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as force_login
from django.contrib.auth import logout as force_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, resolve_url
from django.utils import timezone
from django.utils.html import format_html

import log

from ballotbuddies.alerts.helpers import send_login_email
from ballotbuddies.core.helpers import allow_debug

from .forms import FriendsForm, LoginForm, SignupForm, VoterForm
from .helpers import generate_sample_voters, parse_domain
from .models import Voter


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


def about(request):
    return render(request, "about/index.html")


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
                return redirect(request.GET.get("next") or "buddies:index")

            send_login_email(voter.user)
            domain, standard = parse_domain(voter.user.email)
            context = {
                "domain": domain,
                "standard": standard and request.user_agent.is_pc,  # type: ignore[attr-defined]
            }
            return render(request, "login.html", context)
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
    voter.profile.mark_viewed()

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

    if voter.complete and not voter.updated:
        _updated, error = voter.update_status()
        voter.save()
        if error:
            messages.error(request, error)

    if not messages.get_messages(request):
        for cta in voter.profile_cta:
            messages.info(
                request,
                format_html('{text}: <a href="{url}">{label}</a>', **cta.data),
            )

    form = VoterForm(initial=voter.data, locked=True)
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
def delete(request: HttpRequest):
    if request.method == "POST":
        if "yes" in request.POST:
            request.user.delete()
            messages.info(request, "Your profile has been deleted.")
            return redirect("buddies:about")
        else:
            return redirect("buddies:profile")

    return render(request, "profile/delete.html")


@login_required
def friends(request: HttpRequest):
    assert isinstance(request.user, User)
    voter: Voter = Voter.objects.from_user(request.user)

    if not voter.updated:
        voter.update_status()
        voter.save()

    if request.method == "POST":
        form = FriendsForm(request.POST, required=len(voter.community) < 10)
        if form.is_valid():
            if not form.cleaned_data["emails"]:
                return redirect("buddies:invite")

            voters = Voter.objects.invite(voter, form.cleaned_data["emails"])
            s = "" if len(voters) == 1 else "s"
            messages.success(request, f"Successfully added {len(voters)} friend{s}.")
            return redirect("buddies:friends")
    else:
        form = FriendsForm()

    context = {
        "cta": voter.friends_cta,
        "community": voter.community,
        "recommended": voter.neighbors.all(),
        "form": form,
        "allow_debug": allow_debug(request),
    }
    return render(request, "friends/index.html", context)


@login_required
def friends_search(request: HttpRequest):
    assert isinstance(request.user, User)
    voter: Voter = Voter.objects.from_user(request.user)

    partial = False
    ballot = request.GET.get("ballot") == "yes"
    voted = request.GET.get("voted") != "no"

    queryset = voter.friends.select_related("user")
    if "q" in request.GET:
        partial = True
        queryset = queryset.filter(
            Q(nickname__icontains=request.GET["q"])
            | Q(user__first_name__icontains=request.GET["q"])
            | Q(user__last_name__icontains=request.GET["q"])
            | Q(user__email__icontains=request.GET["q"])
        )
    if ballot:
        queryset = queryset.filter(status__status__ballot=True)
    if not voted:
        queryset = queryset.filter(voted__isnull=True)

    log.info(f"Found {queryset.count()} friend(s) for {partial=} {ballot=} {voted=}")
    community = sorted(queryset, key=lambda voter: voter.display_name.lower())
    context = {
        "community": community,
        "recommended": [],
        "search": True,
        "ballot": ballot,
        "voted": voted,
    }
    if partial:
        return render(request, "friends/_results.html", context)
    return render(request, "friends/index.html", context)


@login_required
def friends_profile(request: HttpRequest, slug: str):
    try:
        voter: Voter = Voter.objects.get(slug=slug)
    except Voter.DoesNotExist:
        messages.error(request, "The requested voter could not be found.")
        return redirect("buddies:friends")

    getattr(voter, "profile")  # ensure Profile exists
    if voter.user == request.user:
        return redirect("buddies:profile")

    if not messages.get_messages(request):
        for cta in voter.profile_cta:
            messages.debug(
                request,
                format_html('{text}: <a href="{url}">{label}</a>', **cta.data),
            )

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


def friends_email(request: HttpRequest, slug: str):
    assert isinstance(request.user, User)
    voter: Voter = Voter.objects.get(slug=slug)
    return JsonResponse({"email": voter.user.email})


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
        if "redirect" in request.POST:
            messages.info(request, "Successfully unfollowed voter.")
            return HttpResponse(
                status=302, headers={"HX-Redirect": resolve_url("buddies:friends")}
            )

    if "add" in request.POST:
        log.info(f"Following voter: {voter}")
        request.user.voter.neighbors.remove(voter)
        request.user.voter.friends.add(voter)
        request.user.voter.save()
        voter.profile.alert(request.user.voter)

    if "absentee" in request.POST:
        log.info(f"Recording in-person intention: {voter}")
        assert request.POST["absentee"] == "false"
        voter.absentee = False
        voter.promoter = request.user.voter
        render_as_table = True

    if "mailed" in request.POST:
        log.info(f"Recording returned ballot: {voter}")
        voter.ballot_returned = timezone.now()
        voter.promoter = request.user.voter
        render_as_table = True

    if "voted" in request.POST:
        log.info(f"Recording vote: {voter}")
        voter.voted = timezone.now()
        voter.promoter = request.user.voter
        render_as_table = True

    if "reset" in request.POST or "reset" in request.GET:
        log.info(f"Clearing vote: {voter}")
        voter.reset_status(promoter=request.user.voter)
        render_as_table = True
        if request.method == "GET":
            voter.save()
            messages.info(request, "Successfully reset ballot status.")
            return redirect("buddies:friends-profile", slug=slug)

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
