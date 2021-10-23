from django.core.management.base import BaseCommand

import log

from ballotbuddies.buddies.models import Voter


class Command(BaseCommand):
    help = "Clean up existing data"

    def handle(self, **_options):
        for voter in Voter.objects.filter(slug=""):
            log.critical("Generating slug for voter")
            voter.save()

        # TODO: only update voters with fewer than 3 pending firends
        for voter in Voter.objects.all():
            if count := voter.update_neighbors():
                self.stdout.write(f"Recommended {count} friend(s) to {voter}")
                voter.save()
