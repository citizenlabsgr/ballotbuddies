from __future__ import annotations

from contextlib import suppress
from datetime import date, timedelta
from functools import cached_property
from itertools import chain
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

import log
import requests
import us
import zipcodes

from ballotbuddies.core.helpers import generate_key, send_invite_email

from .types import Progress, ensure_date


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

    def from_user(self, user: User) -> Voter:
        voter, created = self.get_or_create(user=user)
        if created:
            log.info(f"Created voter: {voter}")
        return voter

    def invite(self, voter: Voter, emails: list[str]) -> list[Voter]:
        friends = []
        for email in emails:
            user, created = User.objects.get_or_create(
                email=email, defaults=dict(username=email)
            )
            if created:
                log.info(f"Created user: {user}")
                send_invite_email(user, voter.user)

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
    updated = models.DateTimeField(null=True, blank=True)
    voted = models.DateTimeField(null=True, blank=True)

    referrer = models.ForeignKey(
        "Voter", null=True, blank=True, on_delete=models.SET_NULL
    )
    friends = models.ManyToManyField("Voter", blank=True, related_name="followers")
    neighbors = models.ManyToManyField("Voter", blank=True, related_name="lurkers")
    strangers = models.ManyToManyField("Voter", blank=True, related_name="blockers")

    objects = VoterManager()

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"

    def __lt__(self, other):
        if self.progress == other.progress:
            return self.display_name.lower() < other.display_name.lower()
        return self.progress > other.progress

    @cached_property
    def email(self) -> str:
        return self.user.email

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
            progress.registered.icon = ""
            progress.registered.url = settings.REGISTRATION_URL.format(
                name=self.state.lower()
            )

        if progress.voted.date and not self.voted:
            self.voted = progress.voted.date
            self.save()

        if self.voted:
            progress.ballot_sent.color = "success"
            progress.ballot_received.color = "success"
            progress.voted.icon = ""
            progress.voted.date = self.voted
            progress.voted.color = "success"

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
        self.voted = None

    def update_status(self) -> tuple[bool, str]:
        previous_status = self._status

        if self.voted and timezone.now() - self.voted > timedelta(weeks=4):
            self.voted = None
            return True, "Reset voted date since the election is in the past."

        if self.state != "Michigan":
            self.updated = timezone.now()
            return False, "Voter registration can only be fetched for Michigan."

        url = settings.STATUS_API + "?" + urlencode(self.data)
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

        return self._status != previous_status, ""

    @property
    def _status(self) -> str:
        return (self.status or {}).get("id", "")

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
    def election(self) -> date | None:
        try:
            return ensure_date(self.status["election"]["date"])
        except (TypeError, KeyError):
            return None

    @property
    def deadline_humanized(self) -> str:
        if self.election:
            delta = timezone.now().date() - self.election
            days = delta.days
            if days > 1:
                return f"{days} days"
            # TODO: Handle past elections
            return "tomorrow" if days == 1 else "today"
        return ""

    @property
    def updated_humanized(self) -> str:
        if self.updated:
            delta = timezone.now() - self.updated
            if delta < timedelta(seconds=5):
                return "Now"
            if delta < timedelta(minutes=5):
                return "Today"
            return f"{self.updated:%-m/%d}"
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
