from django.db import models
from django.utils import timezone

from annoying.fields import AutoOneToOneField

from ballotbuddies.buddies.models import Voter


class Profile(models.Model):

    voter = AutoOneToOneField(Voter, on_delete=models.CASCADE)

    always_alert = models.BooleanField(default=False)

    last_viewed = models.DateTimeField(auto_now_add=True)
    last_alerted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.voter)

    def mark_viewed(self):
        self.last_viewed = timezone.now()
        self.save()
