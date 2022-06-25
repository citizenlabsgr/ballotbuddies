from django.db import models
from django.utils import timezone

import log
from annoying.fields import AutoOneToOneField


class Profile(models.Model):

    voter = AutoOneToOneField("buddies.Voter", on_delete=models.CASCADE)

    always_alert = models.BooleanField(default=False)
    never_alert = models.BooleanField(default=False)
    should_alert = models.BooleanField(default=False, editable=False)

    last_viewed = models.DateTimeField(auto_now_add=True)
    last_alerted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.voter)

    @property
    def last_viewed_days(self) -> int:
        return (timezone.now() - self.last_viewed).days if self.last_viewed else 0

    @property
    def last_alerted_days(self) -> int:
        return (timezone.now() - self.last_alerted).days if self.last_alerted else 0

    def alert(self, voter):
        message, created = Message.objects.get_or_create(profile=self, sent=False)
        if created:
            log.info(f"Drafted new message: {message}")
        message.activity[voter.id] = voter.status["message"]
        message.save()

    def mark_viewed(self, *, save=True):
        self.last_viewed = timezone.now()
        if save:
            self.save()

    def _should_alert(self):
        if self.never_alert:
            return False
        if self.always_alert:
            return True
        if self.last_viewed_days < 30:
            return False
        if self.last_alerted_days < 14:
            return False
        return True

    def mark_alerted(self, *, save=True):
        self.last_alerted = timezone.now()
        if save:
            self.save()

    def save(self, **kwargs):
        self.should_alert = self._should_alert()
        super().save()
        super().save()


class Message(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    activity = models.JSONField(blank=True, default=dict)
    sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True, editable=False)

    def __str__(self):
        return f"{len(self.activity)} activities"

    @property
    def subject(self) -> str:
        return "TODO: subject "

    @property
    def body(self) -> str:
        return "TODO: body"

    def mark_sent(self):
        self.sent = True
        self.sent_at = timezone.now()
        self.save()
