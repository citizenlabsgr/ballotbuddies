from django.core.management.base import BaseCommand

from ballotbuddies.alerts.models import Message
from ballotbuddies.buddies.models import Voter


class Command(BaseCommand):
    help = "Reset voting progress after an election"

    def handle(self, **_options):
        voter: Voter
        for voter in Voter.objects.filter_progressed():
            voter.reset_status()
            voter.save()

        message: Message
        for message in Message.objects.filter_unsent():
            message.clear()
