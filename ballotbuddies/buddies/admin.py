# pylint: disable=unused-argument

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
    messages.info(request, f"Updated {count} voter(s).")


def share_selected_voters(modeladmin, request, queryset):
    count = 0
    voter: Voter
    for voter in queryset:
        count += voter.share_status()
    messages.info(request, f"Shared status to {count} friend(s).")


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):

    search_fields = ["user__email", "user__first_name", "user__last_name"]

    list_filter = ["state", "absentee"]
    list_display = [
        "email",
        "first_name",
        "last_name",
        "birth_date",
        "zip_code",
        "state",
        "status",
        "absentee",
        "voted",
        "updated",
        "created",
    ]

    actions = [update_selected_voters, share_selected_voters]

    filter_horizontal = ["friends", "neighbors", "strangers"]

    readonly_fields = ["status", "absentee", "voted", "updated", "created"]
