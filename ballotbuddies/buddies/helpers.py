from datetime import timedelta
from random import randint

from django.utils import timezone

from .data import SAMPLE_STATUS
from .models import User, Voter
from .types import Progress


def generate_sample_voters(referrer: str = ""):
    if voter := Voter.objects.filter(slug=referrer).first():
        yield voter

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
