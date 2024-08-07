# pylint: disable=unused-variable,redefined-outer-name,expression-not-assigned

from django.urls import reverse
from django.utils import timezone

import pytest
from expecter import expect

from ballotbuddies.core.tests import decode

from ..constants import VOTED
from ..models import User, Voter


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


@pytest.fixture
def friend(voter: Voter):
    user = User.objects.create_user(username="username", password="password")
    voter2 = Voter.objects.from_user(user, VOTED.status)
    voter2.zip_code = "99999"
    voter2.nickname = "Friendo"
    voter2.save()
    voter.friends.add(voter2)
    voter.save()
    return voter2


@pytest.mark.django_db
def describe_profile():
    def it_prompts_to_finish_setup(expect, client, voter):
        client.force_login(voter.user)

        response = client.get("/profile/")
        html = decode(response)
        expect(html).contains("Finish Setup")

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

    def describe_delete():
        @pytest.fixture
        def response(client, voter: Voter):
            client.force_login(voter.user)
            return client.get(reverse("buddies:delete"))

        def describe_GET():
            def it_returns_200(response):
                expect(response.status_code) == 200

            def describe_POST():
                @pytest.fixture
                def post_response(client, response):
                    return client.post(reverse("buddies:delete"), {"yes": ""})

                def it_deletes_voter(post_response, voter: Voter):
                    expect(post_response.status_code) == 302

                    with pytest.raises(Voter.DoesNotExist):
                        Voter.objects.get(user=voter.user)

                def it_redirects_when_unauthenticated(client, response):
                    client.logout()
                    response = client.get(reverse("buddies:delete"))
                    expect(response.status_code) == 302


@pytest.mark.django_db
def describe_friends():
    def describe_index():
        def it_displays_friends(expect, client, voter, friend):
            client.force_login(voter.user)

            response = client.get("/friends/")
            html = decode(response)

            expect(html).contains(friend.nickname)

        def it_can_filter_by_name(expect, client, voter: Voter, friend: Voter):
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
        def it_redirects_for_invalid_slugs(expect, client, voter: Voter):
            client.force_login(voter.user)

            response = client.get("/friends/foobar")

            expect(response.url) == "/friends/"

        def it_handles_incomplete_voters(expect, client, voter: Voter, friend: Voter):
            client.force_login(voter.user)
            voter.status = {}
            voter.save()

            response = client.get(f"/friends/{friend.slug}")
            html = decode(response)

            expect(html).contains(friend.short_name)
            expect(html).contains("Finish Setup")
            expect(html).contains("Never")  # last updated
            expect(html).excludes("None")

        def it_redirects_when_unauthenticated(expect, client, friend: Voter):
            response = client.get(f"/friends/{friend.slug}?referrer=share", follow=True)
            html = decode(response)

            expect(html).contains("Please log in")  # alert
            expect(html).contains("Registered to Vote")  # friends table heading
            expect(html).contains("promote civic engagement")  # custom CTA

            friend.refresh_from_db()
            expect(friend.ballot_shared).is_not(None)

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

            html = decode(response, verbose=False)
            expect(html).includes("I didn't vote")

        def it_can_manually_clear_voting(expect, client, url, voter):
            client.force_login(voter.user)

            response = client.post(url, {"reset": True})

            html = decode(response, verbose=False)
            expect(html).excludes("I didn't vote")

        def it_can_manually_clear_voting_with_redirect(expect, client, url, voter):
            voter.ballot = "http://example.com"
            client.force_login(voter.user)

            response = client.get(url + "?reset=true")
            expect(response.status_code) == 302

            voter.refresh_from_db()
            expect(voter.ballot).is_(None)
