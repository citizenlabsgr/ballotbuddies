from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from django.conf import settings


def to_date(value) -> date:
    if isinstance(value, str):
        value = datetime.strptime(value, "%Y-%m-%d").date()
    return value


def to_ordinal(day: int) -> str:
    return "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


COLOR_VALUES = {
    "success": 3,
    "warning": 2,
    "danger": 1,
    "default": 0,
}

ICON_VALUES = {
    "🔗": 0.32,
    "✅": 0.31,
    "🟡": 0.22,
    "⚠️": 0.21,
    "🚫": 0.1,
    "−": 0.0,
    "": 0.0,
}


@dataclass
class State:

    icon: str = ""
    color: str = "default"
    url: str = ""
    date: date | None = None

    @property
    def value(self) -> float:
        color = self.color.split(" ", maxsplit=1)[0]
        return COLOR_VALUES[color] + ICON_VALUES[self.icon]

    @property
    def short_date(self) -> str:
        self.date = to_date(self.date)
        return f"{self.date:%-m/%-d}" if self.date else ""

    @property
    def full_date(self) -> str:
        self.date = to_date(self.date)
        if self.date:
            ordinal = to_ordinal(self.date.day)
            return f"{self.date:%A, %B %-d}{ordinal}"
        return ""

    @property
    def delta_date(self) -> str:
        if self.icon:
            return self.icon
        self.date = to_date(self.date)
        if self.date:
            delta = (self.date - settings.TODAY).days
            if delta > 1:
                return f"{delta} days"
            if delta == 1:
                return "Tomorrow"
            return self.short_date if delta else "Today"
        return ""

    def __str__(self):
        return f"{self.icon} {self.short_date}".strip()

    def __bool__(self):
        return self.color != "default"


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

    def __eq__(self, other):
        return self.values == other.values

    def __gt__(self, other):
        return self.values > other.values

    @property
    def values(self):
        return (
            self.ballot_received.value,
            self.ballot_sent.value,
            self.voted.value,
            self.ballot_available.value,
            self.registered.value,
        )

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

        delta = to_date(progress.election.date) - settings.TODAY
        if not ballot and delta < timedelta(days=30):
            progress.absentee_approved.color = "success"
            progress.ballot_available.icon = "🚫"
            progress.ballot_available.color = "success text-muted"
            progress.ballot_sent.icon = "−"
            progress.ballot_sent.color = "default text-muted"
            progress.ballot_received.icon = "−"
            progress.ballot_received.color = "default text-muted"
            progress.election.icon = "−"
            progress.election.color = "default text-muted"
            progress.voted.icon = "−"
            progress.voted.color = "default text-muted"

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
            progress.election.color = "success text-muted"
            progress.voted.icon = "✅"
            progress.voted.color = "success"
            progress.voted.date = received_date
        elif sent_date:
            if delta < timedelta(days=7):
                progress.ballot_received.icon = "⚠️"
                progress.ballot_received.color = "warning"
            else:
                progress.ballot_received.icon = "🟡"

        return progress
