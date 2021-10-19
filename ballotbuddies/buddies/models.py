from __future__ import annotations

from typing import List, Tuple
from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

import log
import requests

from ballotbuddies.core.helpers import send_invite_email


class VoterManager(models.Manager):
    def from_user(self, user: User) -> Voter:
        voter, created = self.get_or_create(user=user)
        if created:
            log.info(f"Created voter: {voter}")
        return voter

    def invite(self, voter: Voter, emails: List[str]) -> List[Voter]:
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

    birth_date = models.DateField(null=True, blank=True)
    zip_code = models.CharField(
        null=True, blank=True, max_length=5, verbose_name="ZIP code"
    )

    status = models.JSONField(null=True, blank=True)
    updated = models.DateTimeField(null=True, blank=True)

    referrer = models.ForeignKey(
        "Voter", null=True, blank=True, on_delete=models.SET_NULL
    )
    friends = models.ManyToManyField("Voter", blank=True, related_name="followers")

    objects = VoterManager()

    def __str__(self):
        return f"{self.name} ({self.user.email})"

    @property
    def name(self) -> str:
        return self.user.get_full_name() or self.email

    @property
    def email(self) -> str:
        return self.user.email

    @property
    def first_name(self) -> str:
        return self.user.first_name

    @property
    def last_name(self) -> str:
        return self.user.last_name

    @property
    def data(self) -> dict:
        return dict(
            first_name=self.first_name,
            last_name=self.last_name,
            birth_date=self.birth_date,
            zip_code=self.zip_code,
        )

    @property
    def complete(self) -> bool:
        return all(self.data.values())

    @property
    def progress(self) -> dict:
        values = {}
        status = self.status.get("status", {}) if self.status else {}

        registered = status.get("registered")
        values["registered"] = "✅" if registered else "❌"
        if not registered:
            return values

        if absentee_date := status.get("absentee_application_received"):
            values["absentee_received"] = absentee_date
        else:
            values["absentee_received"] = "-"

        absentee = status.get("absentee")
        values["absentee_approved"] = "✅" if absentee else "⚪"

        values["ballot_available"] = "TBD"
        # TODO: https://github.com/citizenlabsgr/ballotbuddies/issues/17
        ballot = True

        if not ballot and absentee:
            return values

        if sent_date := status.get("absentee_ballot_sent"):
            values["ballot_sent"] = sent_date
        else:
            values["ballot_sent"] = "🟡"

        if received_date := status.get("absentee_ballot_received"):
            values["ballot_received"] = received_date
        elif sent_date:
            values["ballot_received"] = "🟡"

        return values

    def update(self) -> Tuple[bool, str]:
        previous_status = self._status

        url = "https://michiganelections.io/api/status/?" + urlencode(self.data)
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

    def save(self, **kwargs):
        if self.id:
            self.friends.remove(self)
        super().save(**kwargs)
