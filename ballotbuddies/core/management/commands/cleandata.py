from django.core.management.base import BaseCommand

from ballotbuddies.buddies import helpers


class Command(BaseCommand):
    help = "Clean up existing data"

    def handle(self, **_options):
        helpers.update_neighbors()
        helpers.update_statuses()
