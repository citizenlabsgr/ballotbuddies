# pylint: disable=unused-argument,no-self-use

from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    search_fields = [
        "voter__user__email",
        "voter__user__first_name",
        "voter__user__last_name",
    ]

    list_filter = ["always_alert"]
    list_display = [
        "voter",
        "last_viewed",
        "last_viewed_days",
        "last_alerted",
        "last_alerted_days",
        "always_alert",
        "should_alert_",
    ]

    def should_alert_(self, profile: Profile):
        return profile.should_alert

    should_alert_.boolean = True  # type: ignore
    should_alert_.short_description = "Should alert?"  # type: ignore

    readonly_fields = ["last_viewed", "last_alerted"]
