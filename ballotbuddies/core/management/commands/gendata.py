import random
from copy import deepcopy
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.utils import timezone

from ballotbuddies.buddies.constants import BALLOT_PREVIEW_URL
from ballotbuddies.buddies.models import Voter
from ballotbuddies.core.helpers import today

STATUS = {
    "id": "345-3932-11713",
    "status": {
        "absentee": True,
        "ballot": True,
        "registered": True,
        "absentee_ballot_sent": "2021-09-30",
        "absentee_ballot_received": "2021-10-15",
        "absentee_application_received": "2021-09-15",
    },
    "message": "Jane Doe is registered to vote absentee and your ballot was mailed to you on 2021-09-30 for the November Consolidated election on 2021-11-02 and a sample ballot is available.",
    "election": {
        "id": 45,
        "date": "2021-11-02",
        "name": "November Consolidated",
        "description": "",
        "reference_url": None,
    },
    "precinct": {
        "id": 5943,
        "ward": "2",
        "county": "Kent",
        "number": "10",
        "jurisdiction": "City of Kentwood",
    },
    "ballot": {
        "id": 99999,
        "mvic_url": "https://mvic.sos.state.mi.us/Voter/GetMvicBallot/5947/687/",
        "items": 99,
    },
}


class Command(BaseCommand):
    help = "Generate data for automated testing and manual review"

    def add_arguments(self, parser):
        parser.add_argument(
            "voters",
            nargs="?",
            type=lambda value: value.split("/"),
            default=[],
        )

    def handle(self, *, voters, **_options):
        self.update_site()
        self.get_or_create_superuser()
        self.get_or_create_user("newbie@example.com")

        real_voters: list[Voter] = []
        for info in voters:
            voter = self.get_or_create_voter(
                *info.split(","), status=STATUS, admin=True
            )
            real_voters.append(voter)

        voter: Voter
        for voter in Voter.objects.exclude(user__email__contains="example.com"):
            if voter not in real_voters:
                real_voters.append(voter)

        for voter in real_voters:
            voter.friends.clear()
            voter.neighbors.clear()
            voter.strangers.clear()
            voter.save()

        test_voters = list(self.generate_test_voters())

        for count, voter in enumerate(real_voters, start=1):
            _voter: Voter = random.choice(Voter.objects.all())
            status = deepcopy(_voter.status)
            friend = self.get_or_create_voter(
                f"friend+{count}@example.com",
                voter.user.first_name + "'s",
                "Friend",
                str(_voter.birth_date),
                str(_voter.zip_code),
                status=status,
            )
            voter.friends.add(friend, *real_voters, *test_voters)
            voter.save()

        for voter in Voter.objects.all():
            voter.share_status()
            if count := voter.update_neighbors():
                self.stdout.write(f"Recommended {count} friend(s) to {voter}")
                voter.save()

    def update_site(self):
        site = Site.objects.get(id=1)
        site.name = f"Ballot Buddies {settings.BASE_NAME}"  # type: ignore[misc]
        site.domain = settings.BASE_DOMAIN  # type: ignore[misc]
        site.save()
        self.stdout.write(f"Updated site: {site}")

    def get_or_create_superuser(self, username="admin", password="password"):
        try:
            user = User.objects.create_superuser(
                username=username,
                email=f"{username}@{settings.BASE_DOMAIN}",  # type: ignore[misc]
                password=password,
            )
            self.stdout.write(f"Created superuser: {user}")
        except IntegrityError:
            user = User.objects.get(username=username)
            self.stdout.write(f"Found superuser: {user}")

        return user

    def get_or_create_user(self, email: str, password="password"):
        username, _domain = email.split("@")

        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email}
        )
        if created:
            user.set_password(password)
            user.save()

        if created:
            self.stdout.write(f"Created user: {user}")
        else:
            self.stdout.write(f"Updated user: {user}")

        return user

    def get_or_create_voter(
        self,
        base_email: str,
        first_name: str,
        last_name: str,
        birth_date: str,
        zip_code: str,
        *,
        status=None,
        absentee: bool = True,
        ballot: str | None = None,
        admin: bool = False,
    ) -> Voter:
        user = self.get_or_create_user(base_email)
        user.first_name = first_name
        user.last_name = last_name
        if admin:
            user.is_staff = True
            user.is_superuser = True
        user.save()

        voter, created = Voter.objects.update_or_create(
            user=user, defaults=dict(birth_date=birth_date, zip_code=zip_code)
        )

        if created:
            self.stdout.write(f"Created voter: {voter}")
        else:
            self.stdout.write(f"Updated voter: {voter}")

        if status:
            voter.reset_status(absentee=absentee, ballot=ballot, status=status)
            if admin:
                url = BALLOT_PREVIEW_URL.format(ballot_id=status["ballot"]["id"])
                voter.ballot = url
                voter.voted = timezone.now()
            voter.updated = timezone.now() - timedelta(days=1)
            voter.save()

        return voter

    def generate_test_voters(self):
        yield self.get_or_create_voter(
            "test+pending@example.com",
            "New",
            "User",
            "1970-01-01",
            "",
        )

        status = deepcopy(STATUS)
        status["status"]["registered"] = False  # type: ignore
        yield self.get_or_create_voter(
            "test+outstate@example.com",
            "Not",
            "Michigander",
            "1970-01-01",
            "94040",
        )

        status = deepcopy(STATUS)
        status["status"]["registered"] = False  # type: ignore
        yield self.get_or_create_voter(
            "test+unknown@example.com",
            "Not",
            "Registered",
            "1970-01-01",
            "99999",
            status=status,
        )

        status = deepcopy(STATUS)
        status["status"]["absentee_application_received"] = None  # type: ignore
        status["status"]["absentee_ballot_sent"] = None  # type: ignore
        status["status"]["absentee_ballot_received"] = None  # type: ignore
        status["status"]["ballot"] = False  # type: ignore
        yield self.get_or_create_voter(
            "test+lagging@example.com",
            "Absentee",
            "Requested",
            "1970-01-01",
            "99999",
            status=status,
        )

        status = deepcopy(STATUS)
        status["status"]["absentee"] = False  # type: ignore
        status["status"]["absentee_application_received"] = None  # type: ignore
        status["status"]["ballot"] = False  # type: ignore
        yield self.get_or_create_voter(
            "test+missing@example.com",
            "Absentee",
            "Missing",
            "1970-01-01",
            "99999",
            status=status,
        )

        status = deepcopy(STATUS)
        status["status"]["absentee"] = False  # type: ignore
        status["status"]["absentee_application_received"] = None  # type: ignore
        status["status"]["ballot"] = False  # type: ignore
        yield self.get_or_create_voter(
            "test+inperson@example.com",
            "Absentee",
            "Skipped",
            "1970-01-01",
            "99999",
            status=status,
            absentee=False,
        )

        status = deepcopy(STATUS)
        status["status"]["ballot"] = False  # type: ignore
        yield self.get_or_create_voter(
            "test+waiting@example.com",
            "Ballot",
            "Pending",
            "1970-01-01",
            "99999",
            status=status,
        )

        status = deepcopy(STATUS)
        status["status"]["ballot"] = False  # type: ignore
        status["election"]["date"] = today().strftime("%Y-%m-%d")  # type: ignore
        yield self.get_or_create_voter(
            "test+nonvoter@example.com",
            "No",
            "Election",
            "1970-01-01",
            "99999",
            status=status,
        )

        status = deepcopy(STATUS)
        status["status"]["absentee_ballot_sent"] = None  # type: ignore
        yield self.get_or_create_voter(
            "test+available@example.com",
            "Ballot",
            "Available",
            "1970-01-01",
            "99999",
            status=status,
        )

        status = deepcopy(STATUS)
        status["status"]["absentee_ballot_received"] = None  # type: ignore
        yield self.get_or_create_voter(
            "test+holding@example.com",
            "Ballot",
            "Sent",
            "1970-01-01",
            "99999",
            status=status,
        )

        status = deepcopy(STATUS)
        yield self.get_or_create_voter(
            "test+received@example.com",
            "Ballot",
            "Received",
            "1970-01-01",
            "99999",
            status=status,
        )

        status = deepcopy(STATUS)
        status["status"]["absentee"] = False  # type: ignore
        status["status"]["absentee_application_received"] = None  # type: ignore
        yield self.get_or_create_voter(
            "test+walking@example.com",
            "Ballot",
            "Completed",
            "1970-01-01",
            "99999",
            status=status,
            ballot="https://share.michiganelections.io/elections/49/precincts/1193/?proposal-8018=approve",
        )
