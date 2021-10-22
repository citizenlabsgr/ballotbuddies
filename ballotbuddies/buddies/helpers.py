from datetime import timedelta
from random import randint

from django.utils import timezone

from .models import User, Voter
from .types import Progress, State

SAMPLE_STATUS = [
    (
        {"registered": True},
        Progress(
            registered=State(icon="✅", color="success", url="", date=None),
            absentee_received=State(
                icon="−", color="success text-muted", url="", date=None
            ),
            absentee_approved=State(icon="🚫", color="warning", url="", date=None),
            ballot_available=State(icon="🟡", color="default", url="", date=None),
            ballot_sent=State(icon="", color="default", url="", date=None),
            ballot_received=State(icon="", color="default", url="", date=None),
            voted=State(icon="", color="default", url="", date=None),
        ),
    ),
    (
        {"registered": False},
        Progress(
            registered=State(icon="🚫", color="danger", url="", date=None),
            absentee_received=State(icon="", color="default", url="", date=None),
            absentee_approved=State(icon="", color="default", url="", date=None),
            ballot_available=State(icon="", color="default", url="", date=None),
            ballot_sent=State(icon="", color="default", url="", date=None),
            ballot_received=State(icon="", color="default", url="", date=None),
            voted=State(icon="", color="default", url="", date=None),
        ),
    ),
]


def generate_sample_voters():
    user = User(first_name="Jane", last_name="Doe")
    voter = Voter(
        user=user, slug="_", updated=timezone.now() - timedelta(days=randint(7, 180))
    )
    voter.complete = True
    voter.progress = Progress.parse(SAMPLE_STATUS[0][0])
    yield voter

    user = User(first_name="John", last_name="Doe")
    voter = Voter(
        user=user, slug="_", updated=timezone.now() - timedelta(days=randint(7, 180))
    )
    voter.complete = True
    voter.progress = Progress.parse(SAMPLE_STATUS[1][0])
    yield voter
