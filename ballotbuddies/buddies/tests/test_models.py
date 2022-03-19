# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable

from dataclasses import asdict
from datetime import timedelta

from django.utils import timezone

import pytest
from freezegun import freeze_time

from ..data import SAMPLE_DATA
from ..models import User, Voter


def describe_voter():
    @pytest.fixture
    def voter():
        user = User(first_name="Rosalynn", last_name="Bliss")
        return Voter(user=user, birth_date="1975-08-03", zip_code="49503")

    def describe_progress():
        @freeze_time("2021-10-16")
        @pytest.mark.django_db
        @pytest.mark.parametrize(("data", "progress"), SAMPLE_DATA)
        def with_samples(expect, voter, data, progress):
            voter.user.save()

            voter.status = data

            expect(asdict(voter.progress)) == progress

        def with_nonmichigander(expect, voter):
            voter.state = "Ohio"

            expect(
                voter.progress.registered.url
            ) == "https://votesaveamerica.com/state/ohio/"

        def with_manual_voter(expect, voter):
            voter.voted = timezone.now()

            expect(voter.progress.voted.color) == "success"

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

        def with_stale_vote(expect, voter):
            voter.voted = timezone.now() - timedelta(weeks=5)

            updated, error = voter.update_status()

            expect(updated) == True
            expect(error) != ""
            expect(voter.voted) == None

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
