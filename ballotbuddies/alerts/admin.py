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

    list_filter = [
        "always_alert",
        "never_alert",
        "should_alert",
    ]
    list_display = [
        "voter",
        "last_viewed",
        "last_viewed_days",
        "last_alerted",
        "last_alerted_days",
        "always_alert",
        "never_alert",
        "should_alert",
    ]

    readonly_fields = ["last_viewed", "last_alerted"]
