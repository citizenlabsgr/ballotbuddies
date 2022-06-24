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

    # list_filter = []
    list_display = [
        "voter",
    ]

    # actions = []

    # readonly_fields = []
