# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable

from dataclasses import asdict

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

            expect(voter.user.full_name) == "Jane Doe"

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
