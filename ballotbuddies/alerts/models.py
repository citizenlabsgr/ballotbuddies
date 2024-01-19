from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

import log
from annoying.fields import AutoOneToOneField

if TYPE_CHECKING:
    from ballotbuddies.buddies.models import Voter


class Profile(models.Model):
    voter: Voter = AutoOneToOneField("buddies.Voter", on_delete=models.CASCADE)

    always_alert = models.BooleanField(default=False)
    never_alert = models.BooleanField(default=False)

    last_alerted = models.DateTimeField(auto_now_add=True)
    last_viewed = models.DateTimeField(auto_now_add=True)
    staleness = models.DurationField(default=timedelta(days=0), editable=False)
    will_alert = models.BooleanField(default=False, editable=False)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-staleness"]

    def __str__(self):
        return str(self.voter)

    def __repr__(self):
        return repr(self.voter)

    @property
    def has_election(self) -> bool:
        return bool(self.voter.progress.election.date)

    @property
    def message(self) -> Message:
        return Message.objects.get_draft(self)

    @property
    def has_message(self) -> bool:
        return bool(self.message)

    @property
    def should_alert(self) -> bool:
        if self.never_alert:
            return False
        if self.always_alert:
            return True
        if not self.voter.updated:
            # TODO: Remove this case when unsubscribe link is added
            # https://github.com/citizenlabsgr/ballotbuddies/issues/192
            return False
        if self.voter.updated > timezone.now() - timedelta(days=7):
            return False
        if self.voter.complete:
            if not self.has_election:
                return False
            if self.voter.progress.actions:
                if 0 < self.voter.progress.election.days < 7:
                    return self.staleness > timedelta(days=1)
                return self.staleness > timedelta(days=14)
            return self.staleness > timedelta(days=90)
        else:
            return self.staleness > timedelta(days=30)

    def alert(self, voter: Voter, friend: bool = True) -> bool:
        if len(self.message) >= 8:
            return False
        if len(self.message) >= 3 and not friend:
            return False
        self.message.add(voter)
        return True

    def mark_alerted(self, *, save=True):
        self.last_alerted = timezone.now()
        if save:
            self.message.mark_sent()
            self.save()

    def mark_viewed(self, *, save=True):
        self.last_viewed = timezone.now()
        if save:
            if not self.always_alert:
                self.message.mark_read()
            self.save()

    def _staleness(self) -> timedelta:
        now = timezone.now()
        self.last_alerted = self.last_alerted or now
        self.last_viewed = self.last_viewed or now
        delta = min(now - self.last_alerted, now - self.last_viewed)
        return timedelta(days=delta.days)

    def save(self, **kwargs):
        self.staleness = self._staleness()
        if self.pk:
            self.will_alert = self.has_message and self.should_alert
        super().save(**kwargs)


class MessageManager(models.Manager):
    def get_draft(self, profile: Profile):
        message = self.filter(profile=profile, sent=False).first()
        if message is None:
            message = self.create(profile=profile, sent=False)
            log.debug(f"Drafted new message: {message}")
        return message


class Message(models.Model):
    profile: Profile = models.ForeignKey(Profile, on_delete=models.CASCADE)  # type: ignore

    activity = models.JSONField(blank=True, default=dict)
    sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True, editable=False)

    objects = MessageManager()

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        days = self.profile.voter.progress.election.days
        if days == 1:
            _in_days = " Tomorrow"
        elif days > 0:
            _in_days = f" in {days} Days"
        else:
            _in_days = ""
        return f"Your Friends are Preparing to Vote{_in_days}"

    def __bool__(self):
        return bool(self.activity)

    def __len__(self):
        return len(self.activity)

    @property
    def activity_lines(self) -> list[str]:
        return list(self.activity.values())

    @property
    def dismissed(self) -> bool | None:
        if self.sent_at:
            return False
        if self.sent:
            return True
        return None

    def add(self, voter: Voter, *, save=True):
        self.activity[voter.id] = voter.activity
        if save:
            self.save()

    def clear(self):
        log.info(f"Clearing unset message to {self.profile}")
        self.activity = {}
        self.save()

    def mark_sent(self, *, save=True):
        self.sent = True
        self.sent_at = timezone.now()
        if save:
            self.save()

    def mark_read(self, *, save=True):
        self.sent = True
        if save:
            self.save()
