from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Optional

from django.conf import settings
from django.utils import timezone


def ensure_date(value) -> date:
    if isinstance(value, str):
        value = datetime.strptime(value, "%Y-%m-%d").date()
    return value


@dataclass
class State:

    icon: str = ""
    color: str = "default"
    url: str = ""
    date: Optional[date] = None

    @property
    def short_date(self) -> str:
        self.date = ensure_date(self.date)
        return f"{self.date:%-m/%d}" if self.date else ""

    def __str__(self):
        return f"{self.icon} {self.short_date}".strip()


@dataclass
class Progress:

    registered: State = field(default_factory=State)
    absentee_received: State = field(default_factory=State)
    absentee_approved: State = field(default_factory=State)
    ballot_available: State = field(default_factory=State)
    ballot_sent: State = field(default_factory=State)
    ballot_received: State = field(default_factory=State)
    election: State = field(default_factory=State)
    voted: State = field(default_factory=State)

    @classmethod
    def parse(cls, data: dict) -> Progress:
        progress = cls()

        try:
            status = data["status"]
            election = data["election"]
        except (TypeError, KeyError):
            status = {}
            election = {}
        else:
            precinct = data.get("precinct", {})

        progress.election.date = election.get("date")

        if not status:
            progress.registered.icon = "🟡"
            progress.registered.color = "warning"
            return progress

        if registered := status.get("registered"):
            progress.registered.icon = "✅"
            progress.registered.color = "success"
        else:
            progress.registered.icon = "🚫"
            progress.registered.color = "danger"

        if not registered:
            return progress

        if absentee_date := status.get("absentee_application_received"):
            progress.absentee_received.date = absentee_date
            progress.absentee_received.color = "success"
        else:
            progress.absentee_received.icon = "−"
            progress.absentee_received.color = "success text-muted"

        if absentee := status.get("absentee"):
            progress.absentee_approved.icon = "✅"
            progress.absentee_approved.color = "success"
        elif absentee_date:
            progress.absentee_approved.icon = "🟡"
        else:
            progress.absentee_approved.icon = "🚫"
            progress.absentee_approved.url = settings.ABSENTEE_URL
            progress.absentee_approved.color = "warning"
            progress.ballot_sent.icon = "−"
            progress.ballot_received.icon = "−"

        if ballot := status.get("ballot"):
            progress.absentee_approved.color = "success text-muted"
            progress.ballot_available.url = settings.PREVIEW_URL.format(
                election=election["id"],
                precinct=precinct["id"],
                name=data.get("message", "").split(" ")[0],
            )
            progress.ballot_available.color = "success"
            if not absentee:
                progress.voted.icon = "🟡"
        else:
            progress.ballot_available.icon = "🟡"

        delta = ensure_date(progress.election.date) - settings.TODAY
        if not ballot and delta < timedelta(days=30):
            progress.ballot_available.icon = "🚫"
            progress.ballot_available.color = "success text-muted"
            progress.ballot_sent.icon = "−"
            progress.ballot_sent.color = "success text-muted"
            progress.ballot_received.icon = "−"
            progress.ballot_received.color = "success text-muted"
            progress.voted.icon = "−"
            progress.voted.color = "success text-muted"

        if not (ballot and absentee):
            return progress

        if sent_date := status.get("absentee_ballot_sent"):
            progress.ballot_sent.date = sent_date
            progress.ballot_sent.color = "success"
        else:
            progress.ballot_sent.icon = "🟡"

        if not sent_date:
            return progress

        if received_date := status.get("absentee_ballot_received"):
            progress.ballot_received.date = received_date
            progress.ballot_received.color = "success"
        elif sent_date:
            if delta < timedelta(days=7):
                progress.ballot_received.icon = "⚠️"
            else:
                progress.ballot_received.icon = "🟡"

        # TODO: Let voters be manually marked as complete
        # https://github.com/citizenlabsgr/ballotbuddies/issues/55
        if received_date:
            progress.voted.date = timezone.now().date()
            progress.voted.color = "success"

        return progress
