# pylint: disable=unused-argument

from django.contrib import admin, messages
from django.shortcuts import redirect
from django.utils.html import format_html

from ballotbuddies.buddies.models import Voter

from . import helpers
from .models import Message, Profile


class DefaultQueryMixin(admin.ModelAdmin):
    def changelist_view(self, request, *args, **kwargs):
        view = super().changelist_view(request, *args, **kwargs)
        if request.META["QUERY_STRING"]:
            return view
        if request.path in request.META.get("HTTP_REFERER", ""):
            return view
        if query := getattr(self, "default_query"):
            return redirect(request.path + "?" + query)
        return view


def alert_selected_profiles(modeladmin, request, queryset):
    count = 0
    for profile in queryset:
        helpers.send_activity_email(profile.voter.user)
        count += 1
    s = "" if count == 1 else "s"
    messages.success(request, f"Sent {count} email{s}.")


@admin.register(Profile)
class ProfileAdmin(DefaultQueryMixin, admin.ModelAdmin):

    default_query = "will_alert__exact=1"

    search_fields = [
        "voter__nickname",
        "voter__user__email",
        "voter__user__first_name",
        "voter__user__last_name",
    ]

    actions = [alert_selected_profiles]

    list_filter = [
        "always_alert",
        "never_alert",
        "will_alert",
    ]
    list_display = [
        "voter",
        "Can_alert",
        "last_viewed",
        "last_alerted",
        "staleness",
        "Should_alert",
        "will_alert",
    ]

    def Can_alert(self, profile: Profile):
        return profile.can_alert

    Can_alert.boolean = True  # type: ignore

    def Should_alert(self, profile: Profile):
        return profile.should_alert

    Should_alert.boolean = True  # type: ignore

    readonly_fields = [
        "Can_alert",
        "Message",
        "staleness",
        "Should_alert",
        "last_viewed",
        "last_alerted",
    ]

    def Message(self, profile: Profile):
        return format_html("<br><br>".join(profile.message.activity_lines))


def clear_selected_messages(modeladmin, request, queryset):
    count = 0
    message: Message
    for message in queryset:
        message.clear()
        count += 1
    s = "" if count == 1 else "s"
    messages.success(request, f"Cleared {count} message{s}.")


def rebuild_selected_messages(modeladmin, request, queryset):
    count = 0
    message: Message
    for message in queryset:
        if voter_ids := message.activity.keys():
            for voter in Voter.objects.filter(id__in=voter_ids):
                message.add(voter, save=False)
            message.save()
        count += 1
    s = "" if count == 1 else "s"
    messages.success(request, f"Rebuilt {count} message{s}.")


def send_selected_messages(modeladmin, request, queryset):
    count = 0
    message: Message
    for message in queryset:
        helpers.send_activity_email(message.profile.voter.user)
        count += 1
    s = "" if count == 1 else "s"
    messages.success(request, f"Sent {count} email{s}.")


@admin.register(Message)
class MessageAdmin(DefaultQueryMixin, admin.ModelAdmin):

    default_query = "sent__exact=0"

    search_fields = [
        "profile__voter__nickname",
        "profile__voter__user__email",
        "profile__voter__user__first_name",
        "profile__voter__user__last_name",
    ]

    actions = [
        clear_selected_messages,
        rebuild_selected_messages,
        send_selected_messages,
    ]

    list_filter = [
        "sent",
    ]
    list_display = [
        "profile",
        "Activities",
        "sent",
        "sent_at",
        "Dismissed",
        "updated_at",
    ]

    def Activities(self, message: Message):
        return format_html("<br><br>".join(message.activity_lines))

    def Dismissed(self, message: Message):
        return message.dismissed

    Dismissed.boolean = True  # type: ignore

    readonly_fields = [
        "subject",
        "body",
        "sent",
        "sent_at",
        "updated_at",
        "created_at",
    ]
