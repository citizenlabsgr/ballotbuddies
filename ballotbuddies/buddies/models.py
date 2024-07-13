from __future__ import annotations

from contextlib import suppress
from copy import deepcopy
from datetime import timedelta
from functools import cached_property
from itertools import chain
from typing import Iterator
from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

import log
import requests
import us
import zipcodes
from furl import furl

from ballotbuddies.alerts.helpers import send_invite_email, send_voted_email
from ballotbuddies.core.helpers import generate_key

from . import constants
from .types import Message, Progress, to_date

ZERO_WIDTH_SPACE = "\u200b"


class VoterManager(models.Manager):
    def from_email(self, email: str, referrer: str, *, create=True) -> Voter:
        if not create:
            return self.get(user__email=email.lower())  # type: ignore

        try:
            user, created = User.objects.get_or_create(
                email=email.lower(), defaults=dict(username=email)
            )
            if created:
                log.info(f"Created user: {user}")
        except User.MultipleObjectsReturned:
            log.error(f"Multiple users: {email}")
            user = User.objects.filter(email=email).first()  # type: ignore

        voter = self.from_user(user)
        voter.add_friend(referrer)
        return voter

    def from_user(self, user: User, status: dict | None = None) -> Voter:
        voter: Voter
        voter, created = self.get_or_create(user=user)  # type: ignore
        if created:
            log.info(f"Created voter: {voter}")
        if status:
            voter.status = deepcopy(status)
            voter.save()
        return voter

    def from_slug(self, referrer: str) -> Voter | None:
        return self.filter(slug=referrer).first()  # type: ignore

    def invite(self, voter: Voter, emails: list[str]) -> list[Voter]:
        friends = []
        for email in emails:
            user, created = User.objects.get_or_create(
                email=email.lower(), defaults=dict(username=email)
            )
            if created:
                log.info(f"Created user: {user}")
                self.get_or_create(user=user)
            debug = hasattr(user, "profile") and user.profile.always_alert  # type: ignore
            send_invite_email(user, voter, debug=debug)

            other = self.from_user(user)
            other.referrer = other.referrer or voter
            other.friends.add(voter)
            other.save()

            voter.friends.add(other)
            friends.append(other)

        voter.save()
        return friends

    def filter_progressed(self):
        return self.filter(
            models.Q(ballot__isnull=False)
            | models.Q(ballot_updated__isnull=False)
            | models.Q(ballot_returned__isnull=False)
            | models.Q(voted__isnull=False)
        )


class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.CharField(max_length=100, default=generate_key)
    token = models.CharField(max_length=100, default=generate_key)

    nickname = models.CharField(blank=True, max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    zip_code = models.CharField(
        null=True, blank=True, max_length=5, verbose_name="ZIP code"
    )
    state = models.CharField(max_length=20, default="", editable=False)

    status = models.JSONField(null=True, blank=True, editable=False)
    absentee = models.BooleanField(
        default=True, help_text="Voter plans to vote by mail."
    )
    ballot = models.URLField(null=True, blank=True, max_length=2000)
    ballot_updated = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Voter has filled out their sample ballot.",
    )
    ballot_shared = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Voter has shared their completed sample ballot.",
    )
    ballot_returned = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Voter has returned their absentee ballot.",
    )
    voted = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Voter has participated in the upcoming election.",
    )

    referrer = models.ForeignKey(
        "Voter",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referred_voters",
    )
    promoter = models.ForeignKey(
        "Voter",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="promoted_voters",
    )

    friends = models.ManyToManyField("Voter", blank=True, related_name="followers")
    neighbors = models.ManyToManyField("Voter", blank=True, related_name="lurkers")
    strangers = models.ManyToManyField("Voter", blank=True, related_name="blockers")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)
    fetched = models.DateTimeField(null=True, blank=True)

    objects: VoterManager = VoterManager()

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return f"{self.user.get_full_name()} <{self.user.email}>"

    def __lt__(self, other: Voter):
        if self.progress == other.progress:
            return self.display_name.lower() < other.display_name.lower()
        return self.progress > other.progress

    @cached_property
    def legal_name(self) -> str:
        return self.user.get_full_name()

    @cached_property
    def short_name(self) -> str:
        return self.nickname or self.user.first_name

    @cached_property
    def display_name(self) -> str:
        if self.nickname:
            return f"{self.nickname} {self.user.last_name}"
        if name := self.legal_name:
            return name
        return self.user.email

    @cached_property
    def display_name_breakable(self) -> str:
        if "@" in self.display_name:
            email = self.display_name
            for character in ["@", "."]:
                email = email.replace(character, ZERO_WIDTH_SPACE + character)
                return email
        return self.display_name

    @cached_property
    def friends_cta(self) -> str:
        friends = self.friends.count()
        neighbors = self.neighbors.count()
        voters = (
            self.friends.exclude(voted__isnull=True).count()
            + self.neighbors.exclude(voted__isnull=True).count()
        )

        s = "" if friends == 1 else "s"
        text = f"You follow {friends} voter{s}"

        if neighbors:
            s = "" if neighbors == 1 else "s"
            text += f" and have {neighbors} recommended friend{s}"

        if voters:
            have = "has" if voters == 1 else "have"
            text += f". {voters} of them {have} already cast their ballot"
            text += ". Invite more friends to promote democracy!"
        else:
            text += ". Invite more to promote democracy!"

        return text

    @property
    def profile_cta(self) -> Iterator[Message]:
        if not self.complete:
            return
        if not self.progress.registered:
            yield Message(
                "Confirm your voter information matches the SOS",
                "View Registration",
                constants.MICHIGAN_REGISTRATION_URL,
            )
        if not self.progress.actions:
            if not self.voted:
                yield Message(
                    "You have no upcoming elections at this time. "
                    "Check back in a few months for updates!"
                )
            return
        if self.absentee and not self.progress.absentee_requested:
            yield Message(
                "Request your absentee ballot",
                "View Instructions",
                constants.ABSENTEE_URL,
            )
        if not self.ballot and self.ballot_url:
            yield Message(
                "Your sample ballot is ready",
                "View Ballot",
                self.ballot_edit_url,
            )

    @cached_property
    def data(self) -> dict:
        return dict(
            email=self.user.email,
            nickname=self.nickname,
            first_name=self.user.first_name,
            last_name=self.user.last_name,
            birth_date=self.birth_date,
            zip_code=self.zip_code,
        )

    @cached_property
    def elections_api(self) -> str:
        return f"{constants.ELECTIONS_HOST}/api/elections/"

    @cached_property
    def status_api(self) -> str:
        data = self.data.copy()
        data.pop("email")
        data.pop("nickname")
        return f"{constants.ELECTIONS_HOST}/api/status/?{urlencode(data)}"

    @cached_property
    def complete(self) -> bool:
        data = self.data.copy()
        data.pop("email")
        data.pop("nickname")
        return all(data.values())

    @cached_property
    def election(self) -> str:
        return (self.status or {}).get("election", {}).get("name", "")

    @cached_property
    def ballot_url(self) -> str:
        if url := (self.ballot or self.progress.ballot_available.url):
            parts = furl(url)
            parts.args["name"] = self.short_name or "Friend"
            parts.args["slug"] = self.slug
            return parts.url
        return ""

    @cached_property
    def ballot_edit_url(self) -> str:
        if url := self.ballot_url:
            parts = furl(url)
            parts.args["token"] = self.token
            return parts.url
        return ""

    @cached_property
    def ballot_view_url(self) -> str:
        if url := self.ballot_url:
            parts = furl(url)
            parts.args["share"] = "all"
            return parts.url
        return ""

    @cached_property
    def ballot_share_url(self) -> str:
        if url := self.ballot_url:
            parts = furl(url)
            parts.args["share"] = ""
            return parts.url
        return ""

    @cached_property
    def ballot_items(self) -> int:
        return (self.status or {}).get("ballot", {}).get("items", 0)

    @cached_property
    def progress(self) -> Progress:
        progress = Progress.parse(
            self.status,
            completed_ballot=bool(self.ballot),
            shared_ballot=bool(self.ballot_shared),
            returned_date=self.ballot_returned,
            voted=bool(self.voted),
        )

        if self.state != "Michigan":
            if self.complete:
                progress.registered.icon = "🔗"
                progress.registered.url = constants.OTHER_REGISTRATION_URL.format(
                    name=self.state.lower()
                )
            else:
                progress.registered.icon = ""
                progress.registered.color = "default"

        if not self.absentee:
            progress.absentee_requested.icon = "✕"
            progress.absentee_requested.url = ""
            progress.absentee_received.disable()

        if progress.ballot_received.date and not self.ballot_returned:
            log.info(f"Inferring ballot was returned: {self}")
            self.ballot_returned = progress.ballot_received.date_comparable
            self.save()

        if progress.voted.date and not self.voted:
            log.info(f"Recording vote for current election: {self}")
            self.voted = progress.voted.date_comparable
            self.save()
            if self.user.pk and not self.profile.never_alert:
                send_voted_email(self.user)

        if not self.voted and progress.election.date:
            if progress.ballot_completed and not progress.ballot_sent:
                progress.voted.icon = "🟡"
            if progress.ballot_available and progress.election.days <= 0:
                progress.voted.icon = "🟡"

        return progress

    @cached_property
    def activity(self) -> str:
        if self.progress.voted:
            action = "cast their vote"
        elif self.ballot_returned:
            action = "returned their absentee ballot"
        elif self.progress.ballot_sent:
            action = "was mailed their absentee ballot"
        elif self.progress.ballot_completed:
            action = "filled out their sample ballot"
        elif self.progress.ballot_available:
            action = "has a sample ballot available"
        elif self.progress.absentee_received:
            action = "plans to vote by mail"
        elif self.progress.absentee_requested:
            action = "requested an absentee ballot"
        elif self.progress.registered:
            action = "registered to vote"
        else:
            action = "started following you"
        return f"{self.display_name} {action}"

    @cached_property
    def community(self) -> list[Voter]:
        return sorted(
            chain(
                [self],
                self.friends.select_related("user"),
                self.neighbors.select_related("user"),
            )
        )

    def reset_status(self, *, absentee=None, ballot=None, status=None, promoter=None):
        log.info(f"Resetting status: {self}")
        if absentee is not None:
            self.absentee = absentee
        self.ballot = ballot
        self.ballot_updated = None
        self.ballot_shared = None
        self.ballot_returned = None
        self.voted = None
        if status is not None:
            self.status = status
        if promoter:
            self.promoter = promoter
        if not self.user.is_test:  # type: ignore
            self.updated = None

    def update_status(self) -> tuple[bool, str]:
        message = ""
        previous_fingerprint = self.fingerprint

        if self.state != "Michigan":
            self.fetched = timezone.now()
            message = "Voter registration can only be fetched for Michigan."
        elif self.staleness < 60 * 15:
            message = "Voter registration has been fetched recently."
        elif self.user.is_test:  # type: ignore
            message = "Voter registration can only be fetched for real people."
        else:
            log.info(f"GET {self.elections_api}")
            response = requests.get(self.elections_api, timeout=10)
            if response.status_code == 200:
                data = response.json()
                election = data["results"][0]
                log.info(f"200 response: {election}")
                date = to_date(election["date"])
                if date < constants.today():
                    message = "There are no upcoming elections at this time."
            else:
                message = "Election information unavailable at this time."

        if message:
            log.info(message.strip(".") + f": {self}")
            if self.updated is not None:
                return False, message

        log.info(f"GET {self.status_api}")
        response = requests.get(self.status_api, timeout=10)
        if response.status_code == 202:
            data = response.json()
            log.error(f"{response.status_code} response: {data}")
            self.fetched = timezone.now()
            return False, data["message"]
        if response.status_code != 200:
            log.error(f"{response.status_code} response")
            return False, message

        data = response.json()
        log.info(f"{response.status_code} response: {data}")
        self.status = data
        self.fetched = timezone.now()

        changed = self.fingerprint != previous_fingerprint
        if changed or not self.updated:
            self.updated = timezone.now()
            if previous_fingerprint:
                self.share_status()

        return changed, message

    @property
    def fingerprint(self) -> str:
        return (self.status or {}).get("id", "")

    @property
    def staleness(self) -> float:
        delta = timezone.now() - self.updated if self.updated else timedelta(days=1)
        return delta.total_seconds()

    def share_status(self) -> int:
        count = 0
        voter: Voter
        for voter in self.friends.select_related("profile"):
            if voter.profile.alert(self):
                count += 1
        for voter in self.neighbors.select_related("profile"):
            if voter.profile.alert(self, voter.friends.filter(pk=self.pk).exists()):
                count += 1
        return count

    def add_friend(self, referrer: str) -> tuple[Voter | None, bool]:
        voter = Voter.objects.from_slug(referrer)
        if voter is None or voter == self:
            return None, False
        if voter in self.friends.all():
            log.info(f"Friendship exists: {self} + {voter}")
            return voter, False
        log.info(f"Creating friendship: {self} + {voter}")
        self.referrer = self.referrer or voter
        self.friends.add(voter)
        self.save()
        voter.referrer = voter.referrer or self
        voter.friends.add(self)
        voter.save()
        return voter, True

    def update_neighbors(self, *, limit=0) -> int:
        added = 0
        for friend in self.friends.all():
            for voter in friend.friends.all():
                if not any(
                    (
                        voter == self,
                        not voter.complete,
                        self.friends.filter(pk=voter.pk).exists(),
                        self.neighbors.filter(pk=voter.pk).exists(),
                        self.strangers.filter(pk=voter.pk).exists(),
                    )
                ):
                    self.neighbors.add(voter)
                    added += 1
                    if limit and added >= limit:
                        return added
        return added

    @property
    def updated_humanized(self) -> str:
        if self.updated:
            delta = timezone.now() - self.updated
            if delta < timedelta(seconds=5):
                return "Now"
            if delta < timedelta(minutes=5):
                return "Today"
            return f"{self.updated:%-m/%-d}"
        return "−"

    def save(self, **kwargs):
        if self.ballot:
            # TODO: Remove this after 6/20 and not more occurrences
            assert "slug" not in self.ballot, f"Invalid ballot: {self.ballot}"
        if self.user.get_full_name().islower():
            self.user.first_name = self.user.first_name.capitalize()
            self.user.last_name = self.user.last_name.capitalize()
            if self.user.pk:
                self.user.save()
        with suppress(ValueError):
            if places := zipcodes.matching(self.zip_code or "0"):
                abbr = places[0]["state"]
                self.state = us.states.lookup(abbr).name
        if self.id:
            self.friends.remove(self)
        if self.user.pk:
            super().save(**kwargs)
