import os
from datetime import timedelta
from typing import NamedTuple

STATUS_API = "https://michiganelections.io/api/status/"
MICHIGAN_REGISTRATION_URL = "https://mvic.sos.state.mi.us/RegisterVoter/Index"
OTHER_REGISTRATION_URL = "https://votesaveamerica.com/state/{name}/"
ABSENTEE_URL = "https://absentee.michiganelections.io/"
PREVIEW_HOST = os.getenv("PREVIEW_HOST", "https://share.michiganelections.io")
PREVIEW_URL = PREVIEW_HOST + "/elections/{election}/precincts/{precinct}"

REGISTRATION_DEADLINE_DELTA = timedelta(days=15)  # common guidance
ABSENTEE_REQUESTED_DEADLINE_DELTA = timedelta(weeks=4)  # buffer for mail service
ABSENTEE_RECEIVED_DEADLINE_DELTA = timedelta(weeks=2)  # buffer for mail service
BALLOT_AVAILABLE_DEADLINE_DAYS = 30  # SOS is supposed to finalize ballots a month out
BALLOT_AVAILABLE_DEADLINE_DELTA = timedelta(days=BALLOT_AVAILABLE_DEADLINE_DAYS)
BALLOT_COMPLETED_DEADLINE_DELTA = timedelta(days=1)  # common guidance
BALLOT_SENT_DEADLINE_DELTA = timedelta(weeks=3)  # buffer for mail service
BALLOT_RETURNED_DEADLINE_DELTA = timedelta(weeks=2)  # buffer for mail service
BALLOT_RECEIVED_DEADLINE_DELTA = timedelta(days=4)  # Friday before the election
ABSENTEE_WARNING_DAYS = 7  # buffer for mail service
PAST_ELECTION_DAYS = -14


class VoterData(NamedTuple):
    first_name: str
    last_name: str
    status: dict
    progress: dict


UNREGISTERED = VoterData(
    "Ulrich",
    "Unregistered",
    {
        "election": {"date": "2021-11-02"},
        "status": {"registered": False},
    },
    {
        "registered": {
            "icon": "🚫",
            "color": "danger",
            "url": "https://mvic.sos.state.mi.us/RegisterVoter/Index",
            "date": "",
            "deadline": "2021-10-18",
        },
        "absentee_requested": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
            "deadline": "2021-10-05",
        },
        "absentee_received": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
            "deadline": "2021-10-19",
        },
        "ballot_available": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
            "deadline": "2021-10-03",
        },
        "ballot_completed": {
            "color": "default",
            "date": "",
            "deadline": "2021-11-01",
            "icon": "",
            "url": "",
        },
        "ballot_sent": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
            "deadline": "2021-10-12",
        },
        "ballot_returned": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
            "deadline": "2021-10-19",
        },
        "ballot_received": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
            "deadline": "2021-10-29",
        },
        "election": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "2021-11-02",
            "deadline": "",
        },
        "voted": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
            "deadline": "",
        },
    },
)

REGISTERED = VoterData(
    "Reggie",
    "Registered",
    {
        "election": {"date": "2021-11-02"},
        "status": {"registered": True},
    },
    {
        "registered": {
            "icon": "✅",
            "color": "success text-muted",
            "url": "",
            "date": "",
            "deadline": "2021-10-18",
        },
        "absentee_requested": {
            "icon": "🚫",
            "color": "warning",
            "url": "https://absentee.michiganelections.io/",
            "date": "",
            "deadline": "2021-10-05",
        },
        "absentee_received": {
            "icon": "−",
            "color": "default",
            "url": "",
            "date": "",
            "deadline": "2021-10-19",
        },
        "ballot_available": {
            "icon": "🟡",
            "color": "default",
            "url": "",
            "date": "",
            "deadline": "2021-10-03",
        },
        "ballot_completed": {
            "color": "default",
            "date": "",
            "deadline": "2021-11-01",
            "icon": "",
            "url": "",
        },
        "ballot_sent": {
            "icon": "−",
            "color": "default",
            "url": "",
            "date": "",
            "deadline": "2021-10-12",
        },
        "ballot_returned": {
            "icon": "−",
            "color": "default",
            "url": "",
            "date": "",
            "deadline": "2021-10-19",
        },
        "ballot_received": {
            "icon": "−",
            "color": "default",
            "url": "",
            "date": "",
            "deadline": "2021-10-29",
        },
        "election": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "2021-11-02",
            "deadline": "",
        },
        "voted": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
            "deadline": "",
        },
    },
)


VOTED = VoterData(
    "Vicky",
    "Voterson",
    {
        "status": {
            "ballot": True,
            "absentee": True,
            "ballot_url": "https://mvic.sos.state.mi.us/Voter/GetMvicBallot/5947/687/",
            "registered": True,
            "absentee_ballot_sent": "2021-09-30",
            "absentee_ballot_received": "2021-10-15",
            "absentee_application_received": "2021-09-15",
        },
        "message": "Jane Doe is registered to vote absentee and your ballot was mailed to you on 2021-09-30 for the November Consolidated election on 2021-11-02 and a sample ballot is available.",
        "election": {
            "id": 45,
            "date": "2021-11-02",
            "name": "November Consolidated",
            "description": "",
            "reference_url": None,
        },
        "precinct": {
            "id": 5943,
            "ward": "2",
            "county": "Kent",
            "number": "10",
            "jurisdiction": "City of Kentwood",
        },
    },
    {
        "registered": {
            "icon": "✅",
            "color": "success text-muted",
            "url": "",
            "date": "",
            "deadline": "2021-10-18",
        },
        "absentee_requested": {
            "icon": "✅",
            "color": "success text-muted",
            "url": "",
            "date": "",
            "deadline": "2021-10-05",
        },
        "absentee_received": {
            "icon": "",
            "color": "success text-muted",
            "url": "",
            "date": "2021-09-15",
            "deadline": "2021-10-19",
        },
        "ballot_available": {
            "icon": "",
            "color": "success",
            "url": "https://share.michiganelections.io/elections/45/precincts/5943",
            "date": "",
            "deadline": "2021-10-03",
        },
        "ballot_completed": {
            "color": "success text-muted",
            "date": "",
            "deadline": "2021-11-01",
            "icon": "−",
            "url": "",
        },
        "ballot_sent": {
            "icon": "",
            "color": "success text-muted",
            "url": "",
            "date": "2021-09-30",
            "deadline": "2021-10-12",
        },
        "ballot_returned": {
            "icon": "✅",
            "color": "success text-muted",
            "url": "",
            "date": "",
            "deadline": "2021-10-19",
        },
        "ballot_received": {
            "icon": "",
            "color": "success text-muted",
            "url": "",
            "date": "2021-10-15",
            "deadline": "2021-10-29",
        },
        "election": {
            "icon": "−",
            "color": "success text-muted",
            "url": "",
            "date": "2021-11-02",
            "deadline": "",
        },
        "voted": {
            "icon": "✅",
            "color": "success text-muted",
            "url": "",
            "date": "2021-10-15",
            "deadline": "",
        },
    },
)


SAMPLE_DATA: list[VoterData] = [UNREGISTERED, REGISTERED, VOTED]
