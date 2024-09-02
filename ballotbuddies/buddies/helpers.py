from datetime import timedelta
from random import randint

from django.db.models import Count, Q
from django.utils import timezone

import log

from .constants import SAMPLE_DATA
from .models import User, Voter
from .types import Progress


def generate_sample_voters(referrer: str = ""):
    if voter := Voter.objects.filter(slug=referrer).first():
        yield voter

    for value in SAMPLE_DATA:
        user = User(first_name=value.first_name, last_name=value.last_name)
        voter = Voter(
            user=user,
            updated=timezone.now() - timedelta(days=randint(7, 180)),
        )
        voter.complete = True
        voter.progress = Progress.parse(value.status)
        yield voter


def update_neighbors() -> int:
    total = 0

    query = Voter.objects.annotate(pending=Count("neighbors")).filter(pending__lt=3)
    log.info(f"Updating neighbors for {query.count()} voter(s)")
    voter: Voter
    for voter in query:
        if count := voter.update_neighbors(limit=3):
            log.info(f"Recommended {count} friend(s) to {voter}")
            voter.save()
            total += 1

    return total


def update_statuses() -> int:
    total = 0

    age = timezone.now() - timedelta(days=1, hours=1)
    query = Voter.objects.filter(Q(fetched__lte=age) | Q(fetched=None))
    log.info(f"Updating status for {query.count()} voter(s)")
    voter: Voter
    for voter in query:
        if clear_past_election(voter):
            total += 1
        elif voter.update_status()[0]:
            total += 1
        voter.save()

    return total


def clear_past_election(voter: Voter) -> bool:
    past = timezone.now() - timedelta(days=30)
    for field in ["ballot_updated", "ballot_shared", "ballot_returned", "voted"]:
        date = getattr(voter, field)
        if date and date < past:
            log.info(f"Clearing progress for past election: {voter}")
            voter.reset_status()
            return True
    return False
