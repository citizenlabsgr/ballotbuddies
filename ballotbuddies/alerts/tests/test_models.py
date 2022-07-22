# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable,redefined-outer-name


from datetime import timedelta

import pytest

from ballotbuddies.alerts.models import Message, Profile
from ballotbuddies.buddies.constants import REGISTERED
from ballotbuddies.buddies.models import User, Voter


@pytest.fixture
def voter(admin_user):
    return Voter.objects.from_user(admin_user, REGISTERED.status)


@pytest.fixture
def profile(voter):
    return Profile.objects.create(voter=voter)


def describe_profile():
    @pytest.mark.django_db
    def it_can_mark_viewed(expect, profile: Profile):
        profile.mark_viewed()

        expect(profile.staleness) == timedelta(0)
        expect(profile.can_alert) == False
        expect(profile.should_alert) == False

    @pytest.mark.django_db
    def it_can_update_activity(expect, profile: Profile, voter: Voter):
        profile.alert(voter)
        voter.id = voter.id + 1
        profile.alert(voter)

        expect(profile.can_alert) == True
        expect(profile.message.body).contains("2 friends")
        expect(profile.message.body).contains("registered to vote")

    def describe_should_alert():
        def is_false_with_incomplete_voter(expect):
            profile = Profile(voter=Voter(user=User()))

            expect(profile.should_alert) == False


def describe_message():
    def describe_add():
        def it_replaces_legal_name(expect):
            voter = Voter(
                user=User(first_name="Michael", last_name="Doe"),
                status={"message": "Michael Doe is registered to vote."},
                nickname="Mike",
            )

            message = Message()
            message.add(voter, save=False)

            expect(message.body).contains("Mike Doe started following you")

    def describe_dismissed():
        def is_none_by_default(expect):
            message = Message()

            expect(message.dismissed) == None

        def is_false_when_sent(expect):
            message = Message()
            message.mark_sent(save=False)

            expect(message.dismissed) == False

        def is_true_when_read(expect):
            message = Message()
            message.mark_sent(save=False)

            expect(message.dismissed) == False
