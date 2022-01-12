# pylint: disable=unused-argument

from django.contrib import admin, messages

from .models import Voter


def update_selected_voters(modeladmin, request, queryset):
    voter: Voter
    for voter in queryset:
        updated, error = voter.update_status()
        if updated:
            voter.save()
        if error:
            messages.error(request, error)


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):

    search_fields = ["user__email", "user__first_name", "user__last_name"]

    list_filter = ["state"]
    list_display = [
        "email",
        "first_name",
        "last_name",
        "birth_date",
        "zip_code",
        "state",
        "status",
        "updated",
        "voted",
    ]

    actions = [update_selected_voters]

    filter_horizontal = ["friends", "neighbors", "strangers"]
