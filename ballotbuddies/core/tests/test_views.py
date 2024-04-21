# pylint: disable=unused-variable,redefined-outer-name,expression-not-assigned

from django.contrib.messages import get_messages
from django.test import Client

import pytest
from expecter import expect

from ballotbuddies.buddies.constants import VOTED
from ballotbuddies.buddies.models import Voter

from ..models import User
from . import decode


@pytest.fixture
def voter(admin_user: User):
    admin_user.first_name = "Jane"
    admin_user.last_name = "Doe"
    admin_user.save()
    return Voter.objects.from_user(admin_user, VOTED.status)


@pytest.fixture
def friend(voter: Voter):
    user = User.objects.create_user(username="username", password="password")
    voter2 = Voter.objects.from_user(user, VOTED.status)
    voter2.nickname = "Friendo"
    voter2.save()
    voter.friends.add(voter2)
    voter.save()
    return voter2


@pytest.mark.django_db
def describe_index():
    def it_adds_friend_from_referrer(expect, client, voter, friend):
        voter.friends.clear()
        client.force_login(voter.user)

        response = client.get(f"/?referrer={friend.slug}", follow=True)

        html = decode(response)
        expect(html).includes("Successfully added 1 friend.")
        expect(html).includes("Friendo")

        response = client.get(f"/?referrer={friend.slug}", follow=True)

        html = decode(response)
        expect(html).excludes("Successfully added 1 friend.")
        expect(html).includes("Friendo")


@pytest.mark.django_db
def describe_join():
    @pytest.fixture
    def signup_data():
        return {
            "email": "user@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "birth_date": "1990-01-01",
            "zip_code": "12345",
        }

    def it_creates_voter_profile_on_valid_post(client: Client, signup_data):
        response = client.post("/join/", signup_data)

        messages = list(get_messages(response.wsgi_request))
        expect(len(messages)) == 1
        expect(str(messages[0])).contains("created your voter profile")

    def it_redirects_to_login_if_email_exists(client: Client, signup_data):
        Voter.objects.from_email(signup_data["email"], "<referrer>")

        response = client.post("/join/", signup_data)

        messages = list(get_messages(response.wsgi_request))
        expect(len(messages)) == 1
        expect(str(messages[0])).contains("already have an account")


@pytest.mark.django_db
def describe_login():
    def it_displays_button_for_standard_email_domains(expect, client):
        pc_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        response = client.post(
            "/login/", {"email": "test@gmail.com"}, HTTP_USER_AGENT=pc_user_agent
        )

        html = decode(response)
        expect(html).contains("Open gmail.com")

    def it_displays_message_for_non_standard_email_domains(expect, client):
        response = client.post("/login/", {"email": "test@example.com"})

        html = decode(response)
        expect(html).contains("was sent")
