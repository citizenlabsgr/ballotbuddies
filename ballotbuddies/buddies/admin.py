# pylint: disable=unused-argument

from django.contrib import admin

from . import models


def update_selected_voters(modeladmin, request, queryset):
    voter: models.Voter
    for voter in queryset:
        if voter.update():
            voter.save()


@admin.register(models.Voter)
class VoterAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "first_name",
        "last_name",
        "birth_date",
        "zip_code",
        "status",
        "updated",
    ]

    actions = [update_selected_voters]
