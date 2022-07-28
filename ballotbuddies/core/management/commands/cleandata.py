from django.core.management.base import BaseCommand

from ballotbuddies.alerts import helpers as alerts
from ballotbuddies.buddies import helpers as buddies
from ballotbuddies.buddies.models import Voter


class Command(BaseCommand):
    help = "Clean up existing data"

    def handle(self, **_options):
        buddies.update_neighbors()
        buddies.update_statuses()
        alerts.update_profiles()

        # TODO: Remove this once run
        for voter in Voter.objects.all():
            if not voter.complete:
                voter.state = ""
                voter.save()
