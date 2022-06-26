# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable,redefined-outer-name


import pytest

from ballotbuddies.alerts.models import Message, Profile
from ballotbuddies.buddies.models import Voter


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

        expect(profile.last_viewed_days) == 0
        expect(profile.should_alert) == False

    @pytest.mark.django_db
    def it_can_update_activity(expect, profile, voter):
        voter.status = {"message": "Doing stuff"}
        profile.alert(voter)
        voter.id = 2
        voter.status = {"message": "Doing more stuff"}
        profile.alert(voter)

        message: Message = Message.objects.get_draft(profile)
        expect(message.body).contains("2 friends")
