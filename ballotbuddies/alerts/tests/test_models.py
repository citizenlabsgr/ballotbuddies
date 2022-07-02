# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable,redefined-outer-name


from datetime import timedelta

import pytest

from ballotbuddies.alerts.models import Message, Profile
from ballotbuddies.buddies.models import User, Voter


@pytest.fixture
def voter(admin_user):
    return Voter.objects.from_user(admin_user)


@pytest.fixture
def profile(voter):
    return Profile.objects.create(voter=voter)


def describe_profile():
    def it_can_mark_viewed(expect):
        profile = Profile()

        profile.mark_viewed(save=False)

        expect(profile.staleness) == timedelta(0)
        expect(profile.should_alert) == False

    @pytest.mark.django_db
    def it_can_update_activity(expect, profile: Profile, voter: Voter):
        voter.status = {
            "message": "Jane Doe is registered to vote absentee and your "
            "ballot was mailed to you on 2022-06-24 for the State Primary "
            "election on 2022-08-02 and a sample ballot is available."
        }
        profile.alert(voter)
        voter.id = voter.id + 1
        profile.alert(voter)

        expect(profile.message.body).contains("2 friends")
        expect(profile.message.body).contains(
            "Jane Doe is registered to vote absentee and a ballot was mailed to them on 2022-06-24"
        )


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

            expect(message.body).contains("Mike Doe is")

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
