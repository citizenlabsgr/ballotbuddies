# pylint: disable=expression-not-assigned,singleton-comparison,unused-variable


from ballotbuddies.alerts.models import Profile


def describe_profile():
    def it_can_mark_viewed(expect):
        profile = Profile()

        profile.mark_viewed(save=False)

        expect(profile.last_viewed_days) == 0
        expect(profile.should_alert) == False
