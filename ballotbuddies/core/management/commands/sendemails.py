from django.core.management.base import BaseCommand

from ballotbuddies.alerts import helpers as alerts


class Command(BaseCommand):
    help = "Send weekly emails to voters"

    def add_arguments(self, parser):
        parser.add_argument("day", nargs="?")

    def handle(self, day, **_options):
        count = alerts.send_activity_emails(day)
        s = "" if count == 1 else "s"
        self.stdout.write(f"Sent {count} email{s}")
