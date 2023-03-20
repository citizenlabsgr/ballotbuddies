# pylint: disable=redefined-outer-name,unused-variable,unused-argument,expression-not-assigned


from django.utils import timezone

import pytest
from expecter import expect

from ballotbuddies.buddies.constants import VOTED
from ballotbuddies.buddies.models import User, Voter


@pytest.fixture
def voter(admin_user: User):
    admin_user.first_name = "Jane"
    admin_user.last_name = "Doe"
    admin_user.save()
    return Voter.objects.from_user(admin_user, VOTED.status)


@pytest.fixture
def complete_voter(voter: Voter):
    voter.birth_date = timezone.now()
    voter.zip_code = "12345"
    voter.save()
    return voter


def describe_provision_voter():
    @pytest.fixture
    def url():
        return "/api/provision-voter/"

    def describe_POST():
        def it_requires_fields(client, url):
            response = client.post(url)

            expect(response.status_code) == 400
            expect(response.json()) == {
                "errors": {
                    "email": ["This field is required."],
                    "referrer": ["This field is required."],
                    "first_name": ["This field is required."],
                    "last_name": ["This field is required."],
                    "birth_date": ["This field is required."],
                    "zip_code": ["This field is required."],
                }
            }

        @pytest.mark.django_db
        def it_creates_new_voter(client, url, voter: Voter):
            data = {
                "email": "test@example.com",
                "referrer": voter.slug,
                "first_name": "John",
                "last_name": "Doe",
                "birth_date": "1990-01-01",
                "zip_code": "12345",
            }
            response = client.post(url, data)

            expect(response.status_code) == 200
            expect(response.json()) == {"message": "Created voter."}

            user2 = User.objects.get(email="test@example.com")
            voter2 = Voter.objects.get(user=user2)

            expect(voter2.referrer) == voter
            expect(user2.first_name) == "John"
            expect(user2.last_name) == "Doe"
            expect(str(voter2.birth_date)) == "1990-01-01"
            expect(voter2.zip_code) == "12345"

        @pytest.mark.django_db
        def it_handles_existing_voters(client, url, complete_voter: Voter):
            voter = complete_voter
            data = {
                "email": voter.user.email,
                "referrer": voter.slug,
                "first_name": "John",
                "last_name": "Doe",
                "birth_date": "1990-01-01",
                "zip_code": "12345",
            }
            response = client.post(url, data)

            expect(response.status_code) == 200
            expect(response.json()) == {"message": "Found voter."}

            voter.refresh_from_db()

            expect(voter.referrer).is_(None)


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
