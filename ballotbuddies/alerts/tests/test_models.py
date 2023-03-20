# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable,redefined-outer-name


from datetime import timedelta

from django.utils import timezone

import pytest

from ballotbuddies.alerts.models import Message, Profile
from ballotbuddies.buddies.constants import REGISTERED
from ballotbuddies.buddies.models import User, Voter


@pytest.fixture
def voter(admin_user: User):
    v = Voter.objects.from_user(admin_user, REGISTERED.status)
    v.user.first_name = REGISTERED.first_name
    v.user.last_name = REGISTERED.last_name
    v.user.save()
    v.birth_date = "1975-08-03"
    v.zip_code = "49503"
    v.save()
    return v


@pytest.fixture
def profile(voter: Voter):
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

        expect(len(profile.message.activity)) == 1

        voter.id = voter.id + 1
        profile.alert(voter)

        expect(len(profile.message.activity)) == 2

    def describe_should_alert():
        def is_false_with_incomplete_voter(expect):
            profile = Profile(voter=Voter(user=User()))

            expect(profile.should_alert) == False

        def is_false_with_recently_updated_voter(expect, profile: Profile):
            assert profile.voter.complete
            profile.staleness = timedelta(days=99)

            profile.voter.updated = timezone.now() - timedelta(days=6)
            expect(profile.should_alert) == False

            profile.voter.updated = timezone.now() - timedelta(days=8)
            expect(profile.should_alert) == True


def describe_message():
    def describe_str():
        def it_includes_days_to_election(expect, voter):
            message = Message(profile=Profile(voter=voter))

            expect(str(message)) == "Your Friends are Preparing to Vote in 48 Days"

    def describe_add():
        def it_replaces_legal_name(expect):
            voter = Voter(
                user=User(first_name="Michael", last_name="Doe"),
                status={"message": "Michael Doe is registered to vote."},
                nickname="Mike",
                state="Michigan",
            )

            message = Message(profile=Profile(voter=Voter()))
            message.add(voter, save=False)

            expect(message.activity_lines).contains("Mike Doe started following you")

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
