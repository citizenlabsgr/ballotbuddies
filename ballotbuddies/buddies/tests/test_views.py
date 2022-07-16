# pylint: disable=redefined-outer-name,unused-variable,unused-argument,expression-not-assigned

from django.utils import timezone

import log
import pytest

from ..constants import VOTED
from ..models import User, Voter


@pytest.fixture
def voter(admin_user):
    admin_user.first_name = "Jane"
    admin_user.last_name = "Doe"
    admin_user.save()
    return Voter.objects.from_user(admin_user, VOTED.status)


@pytest.fixture
def complete_voter(voter):
    voter.birth_date = timezone.now()
    voter.zip_code = "12345"
    voter.save()
    return voter


@pytest.fixture
def friend(voter):
    user = User.objects.create_user(username="username", password="password")
    voter2 = Voter.objects.from_user(user, VOTED.status)
    voter2.nickname = "Friendo"
    voter2.save()
    voter.friends.add(voter2)
    voter.save()
    return voter2


def decode(response) -> str:
    html = response.content.decode().strip()
    log.info(f"{response.status_code} response:\n\n{html}\n\n")
    return html


@pytest.mark.django_db
def describe_index():
    def it_disables_buttons_when_unauthenticated(expect, client, voter):
        response = client.get("/")

        html = decode(response)
        expect(html).excludes("View Profile")
        expect(html.count("disabled")) == 3

    def it_disables_buttons_with_referrer(expect, client, voter):
        client.force_login(voter.user)

        response = client.get(f"/?referrer={voter.slug}")

        html = decode(response)
        expect(html).excludes("View Profile")
        expect(html.count("disabled")) >= 3  # TODO: should be 4 including the voter


@pytest.mark.django_db
def describe_friends():
    def describe_index():
        def it_displays_friends(expect, client, voter, friend):
            client.force_login(voter.user)

            response = client.get("/friends/")
            html = decode(response)
            expect(html).contains(friend.nickname)

        def it_can_filter_by_name(expect, client, voter, friend):
            client.force_login(voter.user)

            response = client.get("/friends/search/")
            html = decode(response)
            expect(html.count('id="toggle-')) == 1
            expect(html).contains(friend.nickname)

            response = client.get("/friends/search/?q=friend")
            html = decode(response)
            expect(html.count('id="toggle-')) == 1
            expect(html).contains(friend.nickname)

            response = client.get("/friends/search/?q=foobar")
            html = decode(response)
            expect(html.count('id="toggle-')) == 0
            expect(html).excludes(friend.nickname)

    def describe_detail():
        def it_redirects_for_invalid_slugs(expect, client, voter):
            client.force_login(voter.user)

            response = client.get("/friends/foobar")

            expect(response.url) == "/friends/"


@pytest.mark.django_db
def describe_profile():
    def it_redirects_to_finish_setup(expect, client, voter):
        client.force_login(voter.user)

        response = client.get("/profile/")
        expect(response.url) == "/profile/setup/"

    def it_can_update_reminder_emails_preference(expect, client, complete_voter):
        client.force_login(complete_voter.user)

        response = client.get("/profile/")
        html = decode(response)
        expect(html).contains("checked")

        response = client.post("/profile/", follow=True)
        html = decode(response)
        expect(html).excludes("checked")

        response = client.post("/profile/", follow=True)
        html = decode(response)
        expect(html).contains("checked")


@pytest.mark.vcr
@pytest.mark.django_db
def describe_status():
    @pytest.fixture
    def url(voter):
        return f"/friends/{voter.slug}/_status"

    def it_can_manually_record_voting(expect, client, url, voter):
        voter.status["status"]["absentee_ballot_received"] = None
        voter.save()
        client.force_login(voter.user)

        response = client.post(url, {"voted": True})

        html = decode(response)
        expect(html).includes("Didn't vote")

    def it_can_manually_clear_voting(expect, client, url, voter):
        client.force_login(voter.user)

        response = client.post(url, {"reset": True})

        html = decode(response)
        expect(html).excludes("Didn't vote")
