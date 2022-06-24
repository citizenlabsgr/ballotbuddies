from django.db import models

from ballotbuddies.buddies.models import Voter


class Profile(models.Model):

    voter = models.OneToOneField(Voter, on_delete=models.CASCADE)

    always_alert = models.BooleanField(default=False)

    last_viewed = models.DateTimeField(auto_now_add=True)
    last_alerted = models.DateTimeField(auto_now_add=True)
