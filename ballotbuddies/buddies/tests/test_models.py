# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable

import pytest

from ..models import User, Voter


def describe_voter():
    @pytest.fixture
    def voter():
        user = User(first_name="Rosalynn", last_name="Bliss")
        return Voter(user=user, birth_date="1975-08-03", zip_code="49503")

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

    def describe_save():
        @pytest.mark.django_db
        def it_remove_self_from_friends(expect, voter):
            voter.user.save()
            voter.save()

            voter.friends.add(voter)
            voter.save()

            expect(voter.friends.all()).excludes(voter)
