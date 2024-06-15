from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from functools import cached_property

from django.utils import timezone
from django.utils.html import format_html

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
        if deadline := to_date(self.deadline):
            if constants.today() > deadline:
                return False
        return self.icon in {"🟡", "⚠️", "🚫"}

    @property
    def complete(self) -> bool:
        return "success" in self.color or self.icon == "−"

    @property
    def days(self) -> int:
        if self.date:
            delta = to_date(self.date) - constants.today()
            return delta.days
        return 0

    @property
    def date_comparable(self) -> datetime:
        if self.date:
            return timezone.make_aware(to_datetime(self.date))
        return timezone.make_aware(datetime.min)

    @property
    def date_shortened(self) -> str:
        _date = to_date(self.date)
        return f"{_date:%-m/%-d}" if _date else ""

    @property
    def date_delta(self) -> str:
        if self.icon and "success" not in self.color:
            return self.icon
        if _date := to_date(self.date):
            delta = (_date - constants.today()).days
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

    def check(self, when: str = ""):
        self.icon = "✅"
        self.color = "success text-muted"
        if when:
            self.date = when

    def disable(self):
        if self.icon != "✅":
            self.icon = "−"
            self.url = ""
        self.color = "success text-muted"


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
            self.ballot_returned.value,
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
    def percent_scaled(self) -> float:
        return 60 + (40 * self.percent / 100)

    @cached_property
    def actions(self) -> int:
        if self.election.days < 0:
            return 0
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
    def parse(
        cls,
        data: dict,
        *,
        voted: datetime | None = None,
        returned_date: datetime | None = None,
    ) -> Progress:
        progress = cls()

        try:
            status = data["status"] or {}
            election = data["election"] or {}
        except (TypeError, KeyError):
            status = {}
            election = {}
        else:
            precinct = data.get("precinct", {})
            ballot = data.get("ballot", {})

        progress.election.date = election.get("date") or ""
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

        if status.get("registered"):
            progress.registered.check()
        else:
            progress.registered.icon = "🚫"
            progress.registered.color = "danger"
            progress.registered.url = constants.MICHIGAN_REGISTRATION_URL
            if progress.election.days < constants.PAST_ELECTION_DAYS:
                progress.election = State()
            return progress

        if absentee := status.get("absentee"):
            progress.absentee_requested.check()
        elif absentee is None:
            progress.absentee_requested.icon = "−"
            progress.absentee_requested.color = "success text-muted"
        else:
            progress.absentee_requested.icon = "🚫"
            progress.absentee_requested.url = constants.ABSENTEE_URL
            progress.absentee_requested.color = "warning"

        if absentee_date := status.get("absentee_application_received"):
            progress.absentee_received.check(absentee_date)
            if not progress.absentee_requested:
                progress.absentee_requested.disable()
        elif absentee:
            progress.absentee_received.icon = "🚫"
            progress.absentee_received.url = constants.ABSENTEE_URL
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

        if has_ballot := status.get("ballot"):
            progress.absentee_requested.color = "success text-muted"
            progress.absentee_received.color = "success text-muted"
            if ballot:
                progress.ballot_available.url = constants.BALLOT_PREVIEW_URL.format(
                    ballot_id=ballot["id"]
                )
            elif constants.ALLOW_FAKE_DATA:
                progress.ballot_available.url = constants.PRECINCT_PREVIEW_URL.format(
                    election_id=election["id"], precinct_id=precinct["id"]
                )
            progress.ballot_available.check()
            progress.ballot_completed.icon = "🟡"
        else:
            progress.ballot_available.icon = "🟡"

        if voted:
            progress.absentee_received.disable()
            progress.ballot_completed.disable()
            progress.ballot_sent.disable()
            progress.ballot_sent.disable()
            progress.ballot_returned.disable()
            progress.ballot_received.disable()
            progress.election.disable()
            progress.voted.check()

        if (
            not has_ballot
            and progress.election.days < constants.BALLOT_AVAILABLE_DEADLINE_DAYS
        ):
            progress.absentee_requested.color = "success text-muted"
            progress.absentee_received.color = "success text-muted"
            progress.ballot_available.icon = "🚫"
            progress.ballot_available.color = "success text-muted"
            progress.ballot_completed.icon = "−"
            progress.ballot_sent.icon = "−"
            progress.ballot_returned.icon = "−"
            progress.ballot_received.icon = "−"
            progress.election.icon = "−"
            progress.voted.icon = "−"

        if not (has_ballot and absentee_date):
            return progress

        if sent_date := status.get("absentee_ballot_sent"):
            progress.ballot_completed.color = "success text-muted"
            progress.ballot_sent.check(sent_date)
        else:
            progress.ballot_sent.icon = "🟡"

        if not sent_date:
            return progress

        if received_date := status.get("absentee_ballot_received"):
            progress.ballot_completed.icon = "−"
            progress.ballot_sent.color = "success text-muted"
            progress.ballot_returned.check()
            if returned_date:
                progress.ballot_returned.check(to_string(returned_date))
            progress.ballot_received.check(received_date)
            progress.election.disable()
            progress.voted.check(received_date)
        elif returned_date:
            progress.ballot_sent.disable()
            progress.ballot_returned.icon = "✅"
            progress.ballot_returned.date = to_string(returned_date)
            progress.ballot_returned.color = "success"
            progress.ballot_received.icon = "🟡"
            if progress.election.days < constants.ABSENTEE_WARNING_DAYS:
                progress.ballot_received.color = "warning"
        elif sent_date:
            if voted:
                progress.ballot_sent.disable()
            else:
                progress.ballot_returned.icon = "🟡"
                if progress.election.days < constants.ABSENTEE_WARNING_DAYS:
                    progress.ballot_returned.color = "warning"

        return progress


@dataclass
class Message:
    text: str
    label: str = ""
    url: str = ""

    @property
    def data(self) -> dict:
        return asdict(self)

    @property
    def html(self) -> str:
        if self.label and self.url:
            return format_html(
                '{text}: <a href="{url}" class="text-decoration-none">{label}</a>',
                **self.data,
            )
        return format_html("{text}", **self.data)
