# pylint: disable=unused-argument

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
        "always_alert",
        "last_viewed",
        "last_alerted",
    ]

    readonly_fields = ["last_viewed", "last_alerted"]
