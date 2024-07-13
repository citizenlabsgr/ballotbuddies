from django.core.management.base import BaseCommand

from ballotbuddies.alerts import helpers as alerts
from ballotbuddies.friends import helpers as friends


class Command(BaseCommand):
    help = "Clean up existing data"

    def handle(self, **_options):
        friends.update_neighbors()
        friends.update_statuses()
        alerts.update_profiles()
