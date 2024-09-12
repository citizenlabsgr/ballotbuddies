# pylint: disable=unused-argument

import json

from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from .models import Note, Voter


def reset_selected_voters(modeladmin, request, queryset):
    count = 0
    voter: Voter
    for voter in queryset:
        voter.reset_status(promoter=request.user.voter)
        voter.save()
        count += 1
    s = "" if count == 1 else "s"
    messages.info(request, f"Reset {count} voter{s}.")


def update_selected_voters(modeladmin, request, queryset):
    count = 0
    voter: Voter
    for voter in queryset:
        if voter.update_status(force=True)[0]:
            voter.save()
            count += 1
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

    list_filter = [
        "state",
        "absentee",
        "ballot_updated",
        "ballot_shared",
        "ballot_returned",
        "voted",
    ]
    list_display = [
        "display_name",
        "Percent",
        "Actions",
        "absentee",
        "ballot_updated",
        "ballot_shared",
        "ballot_returned",
        "voted",
        "created",
    ]

    def Percent(self, voter: Voter):
        return voter.progress.percent

    def Actions(self, voter: Voter):
        return voter.progress.actions

    actions = [reset_selected_voters, update_selected_voters, share_selected_voters]

    filter_horizontal = ["friends", "neighbors", "strangers"]

    readonly_fields = [
        "state",
        "Status",
        "activity",
        "Percent",
        "Actions",
        "fetched",
        "updated",
        "created",
    ]

    def Status(self, voter: Voter):
        url = voter.status_api
        data = json.dumps(voter.status, indent=4)
        html = f'<a href="{url}" target="_blank">Status API</a><pre>{data}</pre>'
        return mark_safe(html)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["text", "user", "voter", "updated"]
    search_fields = (
        "user__username",
        "user__email",
        "voter__user__username",
        "voter__user__email",
        "text",
    )
    list_filter = ["updated"]
    readonly_fields = ["updated"]
