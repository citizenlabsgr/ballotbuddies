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

    voter = AutoOneToOneField("buddies.Voter", on_delete=models.CASCADE)

    always_alert = models.BooleanField(default=False)
    never_alert = models.BooleanField(default=False)

    last_alerted = models.DateTimeField(auto_now_add=True)
    last_viewed = models.DateTimeField(auto_now_add=True)
    staleness = models.DurationField(default=timedelta(days=0), editable=False)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-staleness"]

    def __str__(self):
        return str(self.voter)

    def __repr__(self):
        return repr(self.voter)

    @property
    def message(self) -> Message:
        return Message.objects.get_draft(self)

    @property
    def can_alert(self) -> bool:
        return bool(self.message)

    @property
    def should_alert(self) -> bool:
        if self.never_alert:
            return False
        if self.always_alert:
            return True
        if not self.voter.complete:
            return False
        if not self.voter.progress.actions:
            return False
        return self.staleness > timedelta(days=14)

    def alert(self, voter: Voter):
        self.message.add(voter)

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
        super().save(**kwargs)


class MessageManager(models.Manager):
    def get_draft(self, profile: Profile):
        created = False
        message = self.filter(profile=profile, sent=False).first()
        if not message:
            message, created = self.get_or_create(profile=profile, sent=False)
        if created:
            log.info(f"Drafted new message: {message}")
        return message


class Message(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    activity = models.JSONField(blank=True, default=dict)
    sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True, editable=False)

    objects = MessageManager()

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        sent = "Sent" if self.sent else "Draft"
        count = len(self.activity)
        activities = "Activity" if count == 1 else "Activities"
        return f"{sent}: {count} {activities}"

    def __bool__(self):
        return bool(self.activity)

    @property
    def subject(self) -> str:
        return "Your Friends are Preparing to Vote"

    @property
    def body(self) -> str:
        count = len(self.activity)
        s = "" if count == 1 else "s"
        have = "has" if count == 1 else "have"
        activity = "  - " + "\n  - ".join(self.activity_lines)
        return (
            f"Your {count} friend{s} on Michigan Ballot Buddies {have} "
            "been making progress towards casting their vote.\n\n"
            f"Here's what they've been up to:\n\n{activity}"
        )

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
        if voter.status:
            text = voter.status["message"]
            text = text.split(" for the")[0]
            text = text.replace("your", "a").replace("you", "them")
            if "@" not in voter.display_name:
                text = text.replace(voter.legal_name, voter.display_name)
        else:
            text = f"{voter.display_name} is planning to vote"

        # pylint: disable=unsupported-assignment-operation
        self.activity[voter.id] = text

        if save:
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
