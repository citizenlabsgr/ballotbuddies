# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable

import pytest

from ..models import User, Voter


def describe_voter():
    @pytest.fixture
    def voter():
        user = User(first_name="Rosalynn", last_name="Bliss")
        return Voter(user=user, birth_date="1975-08-03", zip_code="49503")

    def describe_update():
        @pytest.mark.vcr
        def with_valid_registration(expect, voter):
            voter.status = None

            updated, error = voter.update()

            expect(updated) == True
            expect(error) == ""
