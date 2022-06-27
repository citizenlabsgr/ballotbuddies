# pylint: disable=unused-argument,no-self-use

from django.contrib import admin, messages

from . import helpers
from .models import Message, Profile


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


def send_selected_messages(modeladmin, request, queryset):
    count = 0
    for message in queryset:
        helpers.send_activity_email(message.profile.voter.user)
        count += 1
    messages.success(request, f"Sent {count} email(s).")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    search_fields = [
        "profile__voter__user__email",
        "profile__voter__user__first_name",
        "profile__voter__user__last_name",
    ]

    list_filter = [
        "sent",
    ]
    list_display = [
        "profile",
        "activity_lines",
        "created_at",
        "updated_at",
        "sent",
        "sent_at",
    ]

    readonly_fields = [
        "subject",
        "body",
        "sent",
        "sent_at",
        "created_at",
    ]

    actions = [send_selected_messages]
