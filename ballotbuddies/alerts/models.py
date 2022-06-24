from django.db import models

from ballotbuddies.buddies.models import Voter


class Profile(models.Model):

    voter = models.OneToOneField(Voter, on_delete=models.CASCADE)


#     viewed_at
#     alerted_at
#
#     always_alert
