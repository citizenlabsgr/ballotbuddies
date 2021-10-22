from datetime import timedelta
from random import randint

from django.utils import timezone

from .models import User, Voter
from .types import Progress, State


def generate_sample_voters():
    user = User(first_name="Jane", last_name="Doe")
    voter = Voter(
        user=user, slug="_", updated=timezone.now() - timedelta(days=randint(7, 180))
    )
    voter.complete = True
    voter.progress = Progress(registered=State(icon="✅"))
    yield voter

    user = User(first_name="John", last_name="Doe")
    voter = Voter(
        user=user, slug="_", updated=timezone.now() - timedelta(days=randint(7, 180))
    )
    voter.complete = True
    voter.progress = Progress(registered=State(icon="❌"))
    yield voter
