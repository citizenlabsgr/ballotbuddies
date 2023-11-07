# pylint: disable=unused-argument

import json

from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from .models import Voter


def reset_selected_voters(modeladmin, request, queryset):
    count = 0
    voter: Voter
    for voter in queryset:
        voter.reset_status()
        voter.save()
        count += 1
    s = "" if count == 1 else "s"
    messages.info(request, f"Reset {count} voter{s}.")


def update_selected_voters(modeladmin, request, queryset):
    count = 0
    voter: Voter
    for voter in queryset:
        updated, error = voter.update_status()
        if updated:
            voter.save()
        if error:
            messages.error(request, error)
    s = "" if count == 1 else "s"
    messages.info(request, f"Updated {count} voter{s}.")


def share_selected_voters(modeladmin, request, queryset):
    count = 0
    voter: Voter
    for voter in queryset:
        count += voter.share_status()
    s = "" if count == 1 else "s"
    messages.info(request, f"Shared status {count} times{s}.")


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):

    search_fields = [
        "nickname",
        "user__email",
        "user__first_name",
        "user__last_name",
    ]

    list_filter = ["state", "absentee"]
    list_display = [
        "display_name",
        "Percent",
        "Actions",
        "legal_name",
        "birth_date",
        "zip_code",
        "state",
        "absentee",
        "ballot_returned",
        "voted",
        "fetched",
        "updated",
        "created",
    ]

    def Percent(self, voter: Voter):
        return voter.progress.percent

    def Actions(self, voter: Voter):
        return voter.progress.actions

    actions = [reset_selected_voters, update_selected_voters, share_selected_voters]

    filter_horizontal = ["friends", "neighbors", "strangers"]

    readonly_fields = [
        "Status",
        "Percent",
        "Actions",
        "fetched",
        "updated",
        "created",
    ]

    def Status(self, voter: Voter):
        text = json.dumps(voter.status, indent=4)
        html = f"<pre>{text}</pre>"
        return mark_safe(html)
