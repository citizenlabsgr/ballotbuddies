from django.db import models
from django.utils import timezone

from annoying.fields import AutoOneToOneField

from ballotbuddies.buddies.models import Voter


class Profile(models.Model):

    voter = AutoOneToOneField(Voter, on_delete=models.CASCADE)

    always_alert = models.BooleanField(default=False)
    never_alert = models.BooleanField(default=False)
    should_alert = models.BooleanField(default=False, editable=False)

    last_viewed = models.DateTimeField(auto_now_add=True)
    last_alerted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.voter)

    @property
    def last_viewed_days(self) -> int:
        return (timezone.now() - self.last_viewed).days

    @property
    def last_alerted_days(self) -> int:
        return (timezone.now() - self.last_alerted).days

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

    def mark_viewed(self, *, save=True):
        self.last_viewed = timezone.now()
        if save:
            self.save()

    def save(self, **kwargs):
        self.should_alert = self._should_alert()
        super().save(**kwargs)
