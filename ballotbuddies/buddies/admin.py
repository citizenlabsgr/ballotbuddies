# pylint: disable=unused-argument,no-self-use

from django.contrib import admin, messages

from .models import Voter


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
        "updated",
        "created",
    ]

    def Percent(self, voter: Voter):
        return voter.progress.percent

    def Actions(self, voter: Voter):
        return voter.progress.actions

    actions = [update_selected_voters, share_selected_voters]

    filter_horizontal = ["friends", "neighbors", "strangers"]

    readonly_fields = [
        "status",
        "Percent",
        "Actions",
        "updated",
        "created",
    ]
