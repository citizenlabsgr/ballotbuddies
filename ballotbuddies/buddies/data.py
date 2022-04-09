UNREGISTERED = (
    {
        "election": {"date": "2021-11-02"},
        "status": {"registered": True},
    },
    {
        "registered": {
            "icon": "✅",
            "color": "success",
            "url": "",
            "date": "",
        },
        "absentee_received": {
            "icon": "−",
            "color": "success text-muted",
            "url": "",
            "date": "",
        },
        "absentee_approved": {
            "icon": "🚫",
            "color": "warning",
            "url": "https://absentee.michiganelections.io/",
            "date": "",
        },
        "ballot_available": {
            "icon": "🟡",
            "color": "default",
            "url": "",
            "date": "",
        },
        "ballot_sent": {
            "icon": "−",
            "color": "default",
            "url": "",
            "date": "",
        },
        "ballot_received": {
            "icon": "−",
            "color": "default",
            "url": "",
            "date": "",
        },
        "election": {
            "color": "default",
            "date": "2021-11-02",
            "icon": "",
            "url": "",
        },
        "voted": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
        },
    },
)

REGISTERED = (
    {
        "election": {"date": "2021-11-02"},
        "status": {"registered": False},
    },
    {
        "registered": {
            "icon": "🚫",
            "color": "danger",
            "url": "",
            "date": "",
        },
        "absentee_received": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
        },
        "absentee_approved": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
        },
        "ballot_available": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
        },
        "ballot_sent": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
        },
        "ballot_received": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
        },
        "election": {
            "color": "default",
            "date": "2021-11-02",
            "icon": "",
            "url": "",
        },
        "voted": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
        },
    },
)

REGISTERED_BUT_NO_ELECTION = (
    {
        "status": {
            "ballot": False,
            "absentee": True,
            "ballot_url": None,
            "registered": True,
            "absentee_ballot_sent": None,
            "absentee_ballot_received": None,
            "absentee_application_received": None,
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
            "color": "success",
            "url": "",
            "date": "",
        },
        "absentee_received": {
            "icon": "−",
            "color": "success text-muted",
            "url": "",
            "date": "",
        },
        "absentee_approved": {
            "icon": "✅",
            "color": "success",
            "url": "",
            "date": "",
        },
        "ballot_available": {
            "icon": "🟡",
            "color": "default",
            "url": "",
            "date": "",
        },
        "ballot_sent": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
        },
        "ballot_received": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
        },
        "election": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "2021-11-02",
        },
        "voted": {
            "icon": "",
            "color": "default",
            "url": "",
            "date": "",
        },
    },
)

VOTED = (
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
            "color": "success",
            "url": "",
            "date": "",
        },
        "absentee_received": {
            "icon": "",
            "color": "success",
            "url": "",
            "date": "2021-09-15",
        },
        "absentee_approved": {
            "icon": "✅",
            "color": "success text-muted",
            "url": "",
            "date": "",
        },
        "ballot_available": {
            "icon": "",
            "color": "success",
            "url": "https://share.michiganelections.io/elections/45/precincts/5943?name=Jane",
            "date": "",
        },
        "ballot_sent": {
            "icon": "",
            "color": "success",
            "url": "",
            "date": "2021-09-30",
        },
        "ballot_received": {
            "icon": "",
            "color": "success",
            "url": "",
            "date": "2021-10-15",
        },
        "election": {
            "icon": "",
            "color": "success text-muted",
            "url": "",
            "date": "2021-11-02",
        },
        "voted": {
            "icon": "✅",
            "color": "success",
            "url": "",
            "date": "2021-10-15",
        },
    },
)


SAMPLE_DATA: list[tuple[dict, dict]] = [
    UNREGISTERED,
    REGISTERED,
    REGISTERED_BUT_NO_ELECTION,
    VOTED,
]
