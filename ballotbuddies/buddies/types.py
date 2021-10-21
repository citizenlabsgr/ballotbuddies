from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class State:

    icon: str = ""
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
