from __future__ import annotations

from contextlib import suppress
from datetime import timedelta
from functools import cached_property
from itertools import chain
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

import log
import requests
import us
import zipcodes

from ballotbuddies.alerts.helpers import send_invite_email
from ballotbuddies.core.helpers import generate_key

from . import constants
from .types import Progress, to_datetime

if TYPE_CHECKING:
    from ballotbuddies.alerts.models import Profile


class VoterManager(models.Manager):
    def from_email(self, email: str, referrer: str) -> Voter:
        user, created = User.objects.get_or_create(
            email=email, defaults=dict(username=email)
        )
        if created:
            log.info(f"Created user: {user}")

        voter = self.from_user(user)

        if other := self.filter(slug=referrer).first():
            other.friends.add(voter)
            other.save()

            voter.referrer = voter.referrer or other
            voter.friends.add(other)
            voter.save()

        return voter

    def from_user(self, user: User, status=None) -> Voter:
        voter, created = self.get_or_create(user=user)
        if created:
            log.info(f"Created voter: {voter}")
        if status:
            voter.status = status
            voter.save()
        return voter

    def invite(self, voter: Voter, emails: list[str]) -> list[Voter]:
        friends = []
        for email in emails:
            user, created = User.objects.get_or_create(
                email=email, defaults=dict(username=email)
            )
            profile: Profile = user.profile  # type: ignore
            if created or profile.should_alert:
                log.info(f"Created user: {user}")
                send_invite_email(user, voter.user, debug=profile.always_alert)

            other = self.from_user(user)
            other.referrer = other.referrer or voter
            other.friends.add(voter)
            other.save()

            voter.friends.add(other)
            friends.append(other)

        voter.save()
        return friends


class Voter(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.CharField(max_length=100, default=generate_key)

    birth_date = models.DateField(null=True, blank=True)
    zip_code = models.CharField(
        null=True, blank=True, max_length=5, verbose_name="ZIP code"
    )
    state = models.CharField(max_length=20, default="Michigan", editable=False)

    status = models.JSONField(null=True, blank=True)
    absentee = models.BooleanField(
        default=True, help_text="Voter plans to vote by mail."
    )
    voted = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Voter has participated in the upcoming election.",
    )

    referrer = models.ForeignKey(
        "Voter", null=True, blank=True, on_delete=models.SET_NULL
    )
    friends = models.ManyToManyField("Voter", blank=True, related_name="followers")
    neighbors = models.ManyToManyField("Voter", blank=True, related_name="lurkers")
    strangers = models.ManyToManyField("Voter", blank=True, related_name="blockers")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    objects = VoterManager()

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user.get_full_name()} <{self.user.email}>"

    def __lt__(self, other):
        if self.progress == other.progress:
            return self.display_name.lower() < other.display_name.lower()
        return self.progress > other.progress

    @cached_property
    def email(self) -> str:
        return self.user.email

    @cached_property
    def name(self) -> str:
        return self.first_name or "Friend"

    @cached_property
    def first_name(self) -> str:
        return self.user.first_name

    @cached_property
    def last_name(self) -> str:
        return self.user.last_name

    @cached_property
    def display_name(self) -> str:
        return self.user.display_name  # type: ignore

    @cached_property
    def data(self) -> dict:
        return dict(
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            birth_date=self.birth_date,
            zip_code=self.zip_code,
        )

    @cached_property
    def complete(self) -> bool:
        return all(self.data.values())

    @cached_property
    def progress(self) -> Progress:
        progress = Progress.parse(self.status)

        if self.state != "Michigan":
            progress.registered.icon = "🔗"
            progress.registered.url = constants.OTHER_REGISTRATION_URL.format(
                name=self.state.lower()
            )

        if not self.absentee:
            progress.absentee_requested.icon = "✕"
            progress.absentee_requested.url = ""
            progress.absentee_received.icon = "−"

        if progress.voted.date and not self.voted:
            log.info(f"Recording vote for current election: {self}")
            datetime = to_datetime(progress.voted.date)
            self.voted = timezone.make_aware(datetime)
            self.save()

        if not progress.ballot_available.url and self.voted:
            log.info(f"Clearing recorded vote for past election: {self}")
            self.absentee = True
            self.voted = None
            self.save()

        if self.voted:
            progress.ballot_received.color = "success text-muted"
            progress.election.color = "success text-muted"
            progress.voted.icon = "✅"
            progress.voted.color = "success"
        elif not self.absentee:
            progress.voted.icon = "🟡"

        return progress

    @cached_property
    def community(self) -> list[Voter]:
        return sorted(
            chain(
                [self],
                self.friends.select_related("user"),
                self.neighbors.select_related("user"),
            )
        )

    def reset_status(self):
        self.status = None
        self.updated = None
        self.absentee = True
        self.voted = None

    def update_status(self) -> tuple[bool, str]:
        previous_fingerprint = self.fingerprint

        if self.state != "Michigan":
            self.updated = timezone.now()
            return False, "Voter registration can only be fetched for Michigan."

        url = constants.STATUS_API + "?" + urlencode(self.data)
        log.info(f"GET {url}")
        response = requests.get(url)
        if response.status_code == 202:
            data = response.json()
            log.error(f"{response.status_code} response: {data}")
            self.updated = timezone.now()
            return False, data["message"]
        if response.status_code != 200:
            log.error(f"{response.status_code} response")
            return False, ""

        data = response.json()
        log.info(f"{response.status_code} response: {data}")
        self.status = data
        self.updated = timezone.now()

        changed = self.fingerprint != previous_fingerprint
        if changed and previous_fingerprint:
            self.share_status()

        return changed, ""

    @property
    def fingerprint(self) -> str:
        return (self.status or {}).get("id", "")

    def share_status(self) -> int:
        count = 0
        for friend in self.friends.all():
            friend.profile.alert(self)
            count += 1
        return count

    def update_neighbors(self, limit=0) -> int:
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
        if self.user.get_full_name().islower():
            self.user.first_name = self.user.first_name.capitalize()
            self.user.last_name = self.user.last_name.capitalize()
            self.user.save()
        with suppress(ValueError):
            if places := zipcodes.matching(self.zip_code or "0"):
                abbr = places[0]["state"]
                self.state = us.states.lookup(abbr).name
        if self.id:
            self.friends.remove(self)
        super().save(**kwargs)
