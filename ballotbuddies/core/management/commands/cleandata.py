from django.core.management.base import BaseCommand
from django.db.models import Count

from ballotbuddies.buddies.models import Voter


class Command(BaseCommand):
    help = "Clean up existing data"

    def handle(self, **_options):
        voter: Voter
        for voter in Voter.objects.annotate(pending=Count("neighbors")).filter(
            pending__lt=3
        ):
            if count := voter.update_neighbors(limit=3):
                self.stdout.write(f"Recommended {count} friend(s) to {voter}")
                voter.save()
