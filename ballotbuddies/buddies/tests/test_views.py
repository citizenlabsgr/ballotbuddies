# pylint: disable=redefined-outer-name,unused-variable,unused-argument,expression-not-assigned

import pytest

from ..models import Voter


@pytest.fixture
def voter(admin_user):
    voter, _created = Voter.objects.update_or_create(user=admin_user)
    return voter


@pytest.mark.django_db
def describe_status():
    @pytest.fixture
    def url(voter):
        return f"/friends/{voter.slug}/_status"

    def it_can_manually_record_voting(expect, client, url, voter):
        client.force_login(voter.user)

        response = client.post(url, {"voted": True})

        html = response.content.decode()
        expect(html).excludes("I Voted")

    def it_can_manually_clear_voting(expect, client, url, voter):
        client.force_login(voter.user)

        response = client.post(url, {"reset": True})

        html = response.content.decode()
        expect(html).includes("I Voted")
