from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class State:

    icon: str = ""
    url: str = ""
    date: Optional[date] = None

    @property
    def short_date(self) -> str:
        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, "%Y-%m-%d").date()
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

    @classmethod
    def parse(cls, status: dict) -> Progress:
        progress = cls()

        if not status:
            progress.registered.icon = "🟡"
            return progress

        registered = status.get("registered")
        progress.registered.icon = "✅" if registered else "❌"
        if not registered:
            return progress

        if absentee_date := status.get("absentee_application_received"):
            progress.absentee_received.date = absentee_date
        else:
            progress.absentee_received.icon = "-"

        absentee = status.get("absentee")
        progress.absentee_approved.icon = "✅" if absentee else "⚪"

        ballot = status.get("ballot")
        progress.ballot_available.icon = "✅" if ballot else "🟡"
        progress.ballot_available.url = status.get("ballot_url", "")

        if not (ballot and absentee):
            return progress

        if sent_date := status.get("absentee_ballot_sent"):
            progress.ballot_sent.date = sent_date
            progress.ballot_sent.icon = "✅"
        else:
            progress.ballot_sent.icon = "🟡"

        if not sent_date:
            return progress

        if received_date := status.get("absentee_ballot_received"):
            progress.ballot_received.date = received_date
            progress.ballot_received.icon = "✅"
        elif sent_date:
            progress.ballot_received.icon = "🟡"

        return progress
