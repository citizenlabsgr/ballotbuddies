from contextlib import suppress
from datetime import timedelta
from random import randint

from django.db.models import Count
from django.utils import timezone

import log

from .data import SAMPLE_DATA
from .models import User, Voter
from .types import Progress


def generate_sample_voters(referrer: str = ""):
    if voter := Voter.objects.filter(slug=referrer).first():
        yield voter

    user = User(first_name="Jane", last_name="Doe")
    voter = Voter(
        user=user, slug="1", updated=timezone.now() - timedelta(days=randint(7, 180))
    )
    voter.complete = True
    voter.progress = Progress.parse(SAMPLE_DATA[0][0])
    yield voter

    user = User(first_name="John", last_name="Doe")
    voter = Voter(
        user=user, slug="2", updated=timezone.now() - timedelta(days=randint(7, 180))
    )
    voter.complete = True
    voter.progress = Progress.parse(SAMPLE_DATA[1][0])
    yield voter


def update_neighbors() -> int:
    total = 0

    query = Voter.objects.annotate(pending=Count("neighbors")).filter(pending__lt=3)
    log.info(f"Updating neighboors for {query.count()} voter(s)")
    voter: Voter
    for voter in query:
        if count := voter.update_neighbors(limit=3):
            log.info(f"Recommended {count} friend(s) to {voter}")
            voter.save()
            total += 1

    return total


def update_statuses() -> int:
    total = 0

    age = timezone.now() - timedelta(days=7)
    query = Voter.objects.filter(updated__lte=age)
    log.info(f"Updating status for {query.count()} voter(s)")
    voter: Voter
    for voter in query:
        with suppress(ValueError):
            if voter.update_status()[0]:
                total += 1
        voter.updated = timezone.now()
        voter.save()

    return total
