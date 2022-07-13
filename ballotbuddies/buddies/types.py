from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from functools import cached_property

from ballotbuddies.core.helpers import today

from . import constants


def to_date(value: str) -> date:
    return to_datetime(value).date() if value else value  # type: ignore


def to_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def to_ordinal(day: int) -> str:
    return "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


def to_string(value: datetime) -> str:
    return value.strftime("%Y-%m-%d")


COLOR_VALUES = {
    "success": 3,
    "warning": 2,
    "danger": 1,
    "default": 0,
}

ICON_VALUES = {
    "🔗": 0.32,
    "✅": 0.31,
    "✕": 0.30,
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
    date: str = ""
    deadline: str = ""

    @property
    def value(self) -> float:
        color = self.color.split(" ", maxsplit=1)[0]
        icon = "🔗" if self.url and not self.icon else self.icon
        date_value = ICON_VALUES["✅"] + abs(self.days) / 1000 if self.date else 0
        return COLOR_VALUES[color] + ICON_VALUES[icon] + date_value

    @property
    def actionable(self) -> bool:
        return self.icon in {"🟡", "⚠️", "🚫"}

    @property
    def complete(self) -> bool:
        return "success" in self.color or self.icon == "−"

    @property
    def days(self) -> int:
        if self.date:
            delta = to_date(self.date) - today()
            return delta.days
        return 0

    @property
    def date_shortened(self) -> str:
        _date = to_date(self.date)
        return f"{_date:%-m/%-d}" if _date else ""

    @property
    def date_delta(self) -> str:
        if self.icon:
            return self.icon
        if _date := to_date(self.date):
            delta = (_date - today()).days
            if delta > 1:
                return f"{delta} days"
            if delta == 1:
                return "Tomorrow"
            return self.date_shortened if delta else "Today"
        return ""

    @property
    def date_humanized(self) -> str:
        if _date := to_date(self.date):
            ordinal = to_ordinal(_date.day)
            return f"{_date:%A, %B %-d}{ordinal}"
        return "−"

    @property
    def deadline_humanized(self) -> str:
        if dt := to_date(self.deadline):
            ordinal = to_ordinal(dt.day)
            return f"{dt:%A, %B %-d}{ordinal}"
        return "−"

    def __str__(self):
        return self.date_shortened if self.date else self.icon

    def __bool__(self):
        return self.color != "default" and self.icon not in {"🟡", "⚠️", "🚫"}


@dataclass
class Progress:

    registered: State = field(default_factory=State)
    absentee_requested: State = field(default_factory=State)
    absentee_received: State = field(default_factory=State)
    ballot_available: State = field(default_factory=State)
    ballot_completed: State = field(default_factory=State)
    ballot_sent: State = field(default_factory=State)
    ballot_returned: State = field(default_factory=State)
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
            self.ballot_completed.value,
            self.ballot_sent.value,
            self.voted.value,
            self.ballot_available.value,
            self.absentee_received.value,
            self.absentee_requested.value,
            self.registered.value,
        )

    @cached_property
    def percent(self) -> int:
        if not self.registered.complete:
            return 0
        if not self.election.date:
            return 100
        states = [
            self.registered,
            self.absentee_requested,
            self.absentee_received,
            self.ballot_completed,
            self.ballot_sent,
            self.ballot_returned,
            self.voted,
        ]
        ratio = sum(state.complete for state in states) / len(states)
        return int(ratio * 100)

    @cached_property
    def actions(self) -> int:
        states = [
            self.registered,
            self.absentee_requested,
            self.absentee_received,
            self.ballot_completed,
            self.ballot_sent,
            self.ballot_returned,
            self.ballot_received,
            self.voted,
        ]
        return sum(1 for state in states if state.actionable)

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
        if progress.election.date:
            election_date = to_date(progress.election.date)
            progress.registered.deadline = str(
                election_date - constants.REGISTRATION_DEADLINE_DELTA
            )
            progress.absentee_requested.deadline = str(
                election_date - constants.ABSENTEE_REQUESTED_DEADLINE_DELTA
            )
            progress.absentee_received.deadline = str(
                election_date - constants.ABSENTEE_RECEIVED_DEADLINE_DELTA
            )
            progress.ballot_available.deadline = str(
                election_date - constants.BALLOT_AVAILABLE_DEADLINE_DELTA
            )
            progress.ballot_completed.deadline = str(
                election_date - constants.BALLOT_COMPLETED_DEADLINE_DELTA
            )
            progress.ballot_sent.deadline = str(
                election_date - constants.BALLOT_SENT_DEADLINE_DELTA
            )
            progress.ballot_returned.deadline = str(
                election_date - constants.BALLOT_RETURNED_DEADLINE_DELTA
            )
            progress.ballot_received.deadline = str(
                election_date - constants.BALLOT_RECEIVED_DEADLINE_DELTA
            )

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
            progress.registered.url = constants.MICHIGAN_REGISTRATION_URL

        if not registered:
            return progress

        if absentee := status.get("absentee"):
            progress.absentee_requested.icon = "✅"
            progress.absentee_requested.color = "success"
        else:
            progress.absentee_requested.icon = "🚫"
            progress.absentee_requested.url = constants.ABSENTEE_URL
            progress.absentee_requested.color = "warning"

        if absentee_date := status.get("absentee_application_received"):
            progress.absentee_received.date = absentee_date
            progress.absentee_received.color = "success"
        elif absentee:
            progress.absentee_received.icon = "🚫"
            progress.ballot_sent.icon = "−"
            progress.ballot_returned.icon = "−"
            progress.ballot_received.icon = "−"
        else:
            progress.absentee_received.icon = "−"
            progress.ballot_sent.icon = "−"
            progress.ballot_returned.icon = "−"
            progress.ballot_received.icon = "−"

        if progress.election.days < constants.PAST_ELECTION_DAYS:
            progress.registered.deadline = ""
            progress.absentee_requested.deadline = ""
            progress.absentee_received.deadline = ""
            progress.ballot_available.deadline = ""
            progress.ballot_completed.deadline = ""
            progress.ballot_sent.deadline = ""
            progress.ballot_returned.deadline = ""
            progress.ballot_received.deadline = ""
            progress.election = State()
            return progress

        if ballot := status.get("ballot"):
            progress.absentee_requested.color = "success text-muted"
            progress.absentee_received.color = "success text-muted"
            progress.ballot_available.url = constants.PREVIEW_URL.format(
                election=election["id"], precinct=precinct["id"]
            )
            progress.ballot_available.color = "success"
            progress.ballot_completed.icon = "🚫"
            if not absentee:
                progress.voted.icon = "🟡"
        else:
            progress.ballot_available.icon = "🟡"

        if (
            not ballot
            and progress.election.days < constants.BALLOT_AVAILABLE_DEADLINE_DAYS
        ):
            progress.absentee_requested.color = "success text-muted"
            progress.absentee_received.color = "success text-muted"
            progress.ballot_available.icon = "🚫"
            progress.ballot_available.color = "success text-muted"
            progress.ballot_sent.icon = "−"
            progress.ballot_returned.icon = "−"
            progress.ballot_received.icon = "−"
            progress.election.icon = "−"
            progress.election.date = ""
            progress.voted.icon = "−"

        if not (ballot and absentee_date):
            return progress

        if sent_date := status.get("absentee_ballot_sent"):
            progress.ballot_completed.color = "success text-muted"
            progress.ballot_sent.date = sent_date
            progress.ballot_sent.color = "success"
        else:
            progress.ballot_sent.icon = "🟡"

        if not sent_date:
            return progress

        if received_date := status.get("absentee_ballot_received"):
            progress.ballot_completed.icon = "−"
            progress.ballot_sent.color = "success text-muted"
            progress.ballot_returned.icon = "✅"
            progress.ballot_returned.color = "success text-muted"
            progress.ballot_received.date = received_date
            progress.ballot_received.color = "success text-muted"
            progress.election.color = "success text-muted"
            progress.voted.icon = "✅"
            progress.voted.color = "success"
            progress.voted.date = received_date
        elif sent_date:
            if progress.election.days < constants.ABSENTEE_WARNING_DAYS:
                progress.ballot_returned.icon = "🚫"
                progress.ballot_returned.color = "warning"
            else:
                progress.ballot_returned.icon = "🚫"

        return progress
