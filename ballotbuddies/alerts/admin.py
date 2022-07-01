# pylint: disable=unused-argument,no-self-use

from django.contrib import admin, messages
from django.shortcuts import redirect
from django.utils.html import format_html

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
        "last_alerted",
        "staleness",
        "always_alert",
        "never_alert",
        "should_alert",
        "Can_alert",
    ]

    def Can_alert(self, profile: Profile):
        return profile.can_alert

    Can_alert.boolean = True  # type: ignore

    readonly_fields = ["last_viewed", "last_alerted"]


def send_selected_messages(modeladmin, request, queryset):
    count = 0
    for message in queryset:
        helpers.send_activity_email(message.profile.voter.user)
        count += 1
    messages.success(request, f"Sent {count} email(s).")


@admin.register(Message)
class MessageAdmin(DefaultQueryMixin, admin.ModelAdmin):

    default_query = "sent__exact=0"

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
        "Activities",
        "sent",
        "sent_at",
        "created_at",
        "updated_at",
    ]

    def Activities(self, message: Message):
        return format_html("<br><br>".join(message.activity_lines))

    readonly_fields = [
        "subject",
        "body",
        "sent",
        "sent_at",
        "updated_at",
        "created_at",
    ]

    actions = [send_selected_messages]
