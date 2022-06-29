# pylint: disable=redefined-outer-name,unused-variable,unused-argument,expression-not-assigned

import pytest

from ballotbuddies.buddies.models import Voter


@pytest.fixture
def voter(admin_user):
    return Voter.objects.from_user(admin_user)


@pytest.mark.django_db
def describe_index():
    def it_displays_emails(expect, client, voter):
        client.force_login(voter.user)

        response = client.get("/emails/")

        html = response.content.decode()
        expect(html).contains("Join Firstname Lastname on Michigan Ballot Buddies")


@pytest.mark.django_db
def describe_detail():
    def it_displays_emails(expect, client, voter):
        client.force_login(voter.user)

        response = client.get(f"/emails/{voter.slug}")

        html = response.content.decode()
        expect(html).contains(voter.user.email)
