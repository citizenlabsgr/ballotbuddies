# pylint: disable=redefined-outer-name,unused-variable,unused-argument,expression-not-assigned


import pytest
from expecter import expect

from ballotbuddies.buddies.models import Voter


@pytest.fixture
def voter(admin_user):
    return Voter.objects.from_user(admin_user)


def describe_update_ballot():
    @pytest.fixture
    def url():
        return "/api/update-ballot/"

    def describe_POST():
        def it_requires_slug_and_url(client, url):
            response = client.post(url)

            expect(response.status_code) == 400
            expect(response.json()) == {
                "errors": {
                    "voter": ["This field is required."],
                    "url": ["This field is required."],
                }
            }

        @pytest.mark.django_db
        def it_updates_voters_ballot(client, url, voter):
            data = {"voter": voter.slug, "url": "http://example.com"}
            response = client.post(url, data)

            expect(response.status_code) == 200
            expect(response.json()) == {
                "message": "Successfully updated voter's ballot."
            }

            voter.refresh_from_db()
            expect(voter.ballot) == "http://example.com"

        @pytest.mark.django_db
        def it_handles_unknown_voters(client, url):
            data = {"voter": "foobar", "url": "http://example.com"}
            response = client.post(url, data)

            expect(response.status_code) == 404
