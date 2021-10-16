# pylint: disable=unused-argument

from django.contrib import admin

from .models import Voter


def update_selected_voters(modeladmin, request, queryset):
    voter: Voter
    for voter in queryset:
        if voter.update():
            voter.save()


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):

    list_display = [
        "email",
        "first_name",
        "last_name",
        "birth_date",
        "zip_code",
        "status",
        "updated",
    ]

    actions = [update_selected_voters]
