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
    def it_can_update_activity(expect, profile: Profile, voter: Voter):
        voter.status = {
            "message": "Jane Doe is registered to vote absentee and your "
            "ballot was mailed to you on 2022-06-24 for the State Primary "
            "election on 2022-08-02 and a sample ballot is available."
        }
        profile.alert(voter)
        voter.id = 2
        profile.alert(voter)

        message: Message = Message.objects.get_draft(profile)
        expect(message.body).contains("2 friends")
        expect(message.body).contains(
            "Jane Doe is registered to vote absentee and a ballot was mailed to them on 2022-06-24"
        )
