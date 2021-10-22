from django.core.management.base import BaseCommand

import log

from ballotbuddies.buddies.models import Voter


class Command(BaseCommand):
    help = "Clean up existing data"

    def handle(self, **_options):
        for voter in Voter.objects.filter(slug=""):
            log.critical("Generating slug for voter")
            voter.save()
