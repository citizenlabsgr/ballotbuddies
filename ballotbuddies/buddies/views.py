import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, resolve_url
from django.utils import timezone

import log

from .forms import FriendsForm, VoterForm
from .models import Note, Voter

###############################################################################
# Profile


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
        _updated, message = voter.update_status()
        voter.save()
        if message:
            messages.error(request, message)

    if not messages.get_messages(request):
        for cta in voter.profile_cta:
            messages.warning(request, cta.html)

    form = VoterForm(initial=voter.data, locked=True)
    context = {"voter": voter, "form": form}
    return render(request, "profile/detail.html", context)


@login_required
def profile_setup(request: HttpRequest):
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
def profile_unsubscribe(request: HttpRequest):
    assert isinstance(request.user, User)
    voter: Voter = Voter.objects.from_user(request.user)
    voter.profile.never_alert = True
    voter.profile.save()
    messages.info(request, "You have been unsubscribed from periodic reminder emails.")
    return redirect("buddies:profile")


@login_required
def profile_delete(request: HttpRequest):
    if request.method == "POST":
        if "yes" in request.POST:
            request.user.delete()
            messages.info(request, "Your profile has been deleted.")
            return redirect("core:about")
        else:
            return redirect("buddies:profile")

    return render(request, "profile/delete.html")


###############################################################################
# Friends


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
    }
    return render(request, "friends/index.html", context)


@login_required
def friends_search(request: HttpRequest):
    assert isinstance(request.user, User)
    voter: Voter = Voter.objects.from_user(request.user)

    partial = False
    ballot = request.GET.get("ballot") == "yes"
    voted = request.GET.get("voted") != "no"

    queryset = voter.friends.filter(
        Q(state="Michigan") | Q(zip_code="99999") | Q(zip_code="")
    ).select_related("user")
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
    context = {
        "community": sorted(queryset, reverse=True),
        "recommended": [],
        "search": True,
        "ballot": ballot,
        "voted": voted,
    }
    if partial:
        return render(request, "friends/_results.html", context)
    return render(request, "friends/index.html", context)


def friends_profile(request: HttpRequest, slug: str):
    if referrer := request.GET.get("referrer") or request.META.get("HTTP_REFERER"):
        log.info(f"Returned to profile {slug=} from {referrer=}")

    try:
        voter: Voter = Voter.objects.get(slug=slug)
    except Voter.DoesNotExist:
        messages.error(request, "The requested voter could not be found.")
        return redirect("buddies:friends")

    getattr(voter, "profile")  # ensure Profile exists
    if voter.user == request.user:
        return redirect("buddies:profile")
    else:
        request.session["referrer"] = voter.slug

    if referrer and "share" in referrer:
        log.info(f"{request.user} viewed shared ballot of {voter}")
        previously_shared = bool(voter.ballot_shared)
        voter.ballot_shared = timezone.now()
        voter.save()
        if not previously_shared:
            voter.share_status()

    if not request.user.is_authenticated:
        messages.info(request, "Please log in to view your friend's profile.")
        return redirect("core:index")

    if not messages.get_messages(request):
        for cta in voter.profile_cta:
            messages.debug(request, cta.html)

    form = VoterForm(initial=voter.data, locked=True)
    context = {
        "voter": voter,
        "form": form,
        "note": Note.objects.get_or_blank(request.user, voter),
    }
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
def friends_status(request: HttpRequest, slug: str):
    assert isinstance(request.user, User)
    voter: Voter = Voter.objects.get(slug=slug)
    render_as_table = request.method == "GET"
    start = time.time()

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
        log.info(f"Recording absentee intention: {voter}")
        voter.absentee = request.POST["absentee"] == "true"
        voter.promoter = request.user.voter
        voter.updated = timezone.now()
        voter.save()
        render_as_table = True

    if "mailed" in request.POST:
        log.info(f"Recording returned ballot: {voter}")
        voter.ballot_returned = timezone.now()
        voter.promoter = request.user.voter
        voter.updated = timezone.now()
        voter.save()
        voter.share_status()
        render_as_table = True

    if "voted" in request.POST:
        log.info(f"Recording vote: {voter}")
        voter.voted = timezone.now()
        voter.promoter = request.user.voter
        voter.updated = timezone.now()
        voter.save()
        voter.share_status()
        render_as_table = True

    if "reset" in request.POST or "reset" in request.GET:
        log.info(f"Clearing vote: {voter}")
        voter.reset_status(promoter=request.user.voter)
        voter.save()
        render_as_table = True
        if request.method == "GET":
            messages.info(request, "Successfully reset ballot status.")
            return redirect("buddies:friends-profile", slug=slug)

    if render_as_table:
        template_name = "profile/_table.html"
        while time.time() - start < 1.0:
            time.sleep(0.1)
    else:
        template_name = "friends/_row.html"
    context = {"voter": voter, "recommended": []}
    return render(request, template_name, context)


@login_required
def friends_note(request: HttpRequest, slug: str):
    assert isinstance(request.user, User)
    voter = Voter.objects.get(slug=slug)
    Note.objects.update_text(request.user, voter, request.POST["text"])
    return HttpResponse()


@login_required
def friends_invite(request: HttpRequest):
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
