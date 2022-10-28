# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable

from dataclasses import asdict

from django.conf import settings
from django.utils import timezone

import pytest

from ..constants import REGISTERED, SAMPLE_DATA, UNREGISTERED, VOTED
from ..models import User, Voter


def describe_voter():
    @pytest.fixture
    def voter():
        user = User(first_name="Rosalynn", last_name="Bliss")
        return Voter(
            user=user, birth_date="1975-08-03", zip_code="49503", state="Michigan"
        )

    def describe_progress():
        @pytest.mark.django_db
        @pytest.mark.parametrize("sample", SAMPLE_DATA)
        def with_samples(expect, voter, sample):
            voter.user.save()

            voter.status = sample.status

            expect(asdict(voter.progress)) == sample.progress

        def with_non_michigander(expect, voter):
            voter.state = "Ohio"

            expect(
                voter.progress.registered.url
            ) == "https://votesaveamerica.com/state/ohio/"

        @pytest.mark.django_db
        def with_past_election(expect, voter, monkeypatch):
            monkeypatch.setattr(settings, "TODAY", None)
            voter.voted = timezone.now()
            voter.user.save()

            voter.status = VOTED.status

            expect(voter.progress.voted.date) == ""
            expect(voter.voted) == None

        @pytest.mark.django_db
        def with_planned_present_voter(expect, voter):
            voter.status = REGISTERED.status
            voter.absentee = False
            voter.ballot = "http://example.com"
            voter.user.save()

            expect(voter.progress.voted.icon) == "🟡"

        @pytest.mark.django_db
        def with_completed_present_voter(expect, voter):
            voter.status = VOTED.status
            voter.voted = timezone.now()
            voter.user.save()

            expect(voter.progress.voted.color) == "success text-muted"

    def describe_activity():
        @pytest.mark.django_db
        @pytest.mark.parametrize(
            ("status", "activity"),
            [
                (UNREGISTERED.status, "Rosalynn Bliss started following you"),
                (REGISTERED.status, "Rosalynn Bliss registered to vote"),
                (VOTED.status, "Rosalynn Bliss cast their vote"),
            ],
        )
        def with_samples(expect, voter, status, activity):
            voter.user.save()

            voter.status = status

            expect(voter.activity) == activity

    def describe_update_status():
        @pytest.mark.vcr
        def with_valid_registration(expect, voter):
            voter.status = None

            updated, error = voter.update_status()

            expect(updated) == True
            expect(error) == ""

        @pytest.mark.vcr
        def with_invalid_registration(expect, voter):
            voter.zip_code = ""
            voter.status = None

            updated, error = voter.update_status()

            expect(updated) == False
            expect(error) == ""

    def describe_update_neighbors():
        @pytest.mark.django_db
        def it_returns_count_of_added_neighbors(expect, voter):
            voter.user.save()
            voter.save()

            count = voter.update_neighbors()

            expect(count) == 0

    def describe_save():
        @pytest.mark.django_db
        def it_formats_name(expect, voter):
            voter.user.first_name = "jane"
            voter.user.last_name = "doe"
            voter.user.save()

            voter.save()

            expect(voter.user.get_full_name()) == "Jane Doe"

        @pytest.mark.django_db
        def it_remove_self_from_friends(expect, voter):
            voter.user.save()
            voter.save()

            voter.friends.add(voter)
            voter.save()

            expect(voter.friends.all()).excludes(voter)

        @pytest.mark.django_db
        def it_updates_state(expect, voter):
            voter.user.save()

            voter.zip_code = "94040"
            voter.save()

            expect(voter.state) == "California"

        @pytest.mark.django_db
        def it_handles_invalid_zip_code(expect, voter):
            voter.user.save()

            voter.zip_code = "?????"
            voter.save()

            expect(voter.state) == "Michigan"
