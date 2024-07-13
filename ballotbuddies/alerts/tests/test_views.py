# pylint: disable=redefined-outer-name,unused-variable,expression-not-assigned

import pytest

from ballotbuddies.friends.constants import VOTED
from ballotbuddies.friends.models import User, Voter


@pytest.fixture
def voter(admin_user: User):
    admin_user.first_name = "Jane"
    admin_user.last_name = "Doe"
    admin_user.save()
    return Voter.objects.from_user(admin_user, VOTED.status)


@pytest.mark.django_db
def describe_index():
    def it_displays_emails(expect, client, voter: Voter):
        client.force_login(voter.user)

        response = client.get("/debug/")

        html = response.content.decode()
        expect(html).contains("Join Firstname Lastname on Ballot Buddies")


@pytest.mark.django_db
def describe_detail():
    def it_displays_emails(expect, client, voter: Voter):
        client.force_login(voter.user)

        response = client.get(f"/debug/{voter.slug}")

        html = response.content.decode()
        expect(html).contains(voter.user.email)
