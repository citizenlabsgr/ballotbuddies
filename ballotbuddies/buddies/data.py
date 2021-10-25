SAMPLE_DATA = [
    (
        {
            "election": {"date": "2021-11-02"},
            "status": {"registered": True},
        },
        {
            "registered": {"icon": "✅", "color": "success", "url": "", "date": None},
            "absentee_received": {
                "icon": "−",
                "color": "success text-muted",
                "url": "",
                "date": None,
            },
            "absentee_approved": {
                "icon": "🚫",
                "color": "warning",
                "url": "",
                "date": None,
            },
            "ballot_available": {
                "icon": "🟡",
                "color": "default",
                "url": "",
                "date": None,
            },
            "ballot_sent": {"icon": "−", "color": "default", "url": "", "date": None},
            "ballot_received": {
                "icon": "−",
                "color": "default",
                "url": "",
                "date": None,
            },
            "election": {
                "color": "default",
                "date": "2021-11-02",
                "icon": "",
                "url": "",
            },
            "voted": {"icon": "", "color": "default", "url": "", "date": None},
        },
    ),
    (
        {
            "election": {"date": "2021-11-02"},
            "status": {"registered": False},
        },
        {
            "registered": {"icon": "🚫", "color": "danger", "url": "", "date": None},
            "absentee_received": {
                "icon": "",
                "color": "default",
                "url": "",
                "date": None,
            },
            "absentee_approved": {
                "icon": "",
                "color": "default",
                "url": "",
                "date": None,
            },
            "ballot_available": {
                "icon": "",
                "color": "default",
                "url": "",
                "date": None,
            },
            "ballot_sent": {"icon": "", "color": "default", "url": "", "date": None},
            "ballot_received": {
                "icon": "",
                "color": "default",
                "url": "",
                "date": None,
            },
            "election": {
                "color": "default",
                "date": "2021-11-02",
                "icon": "",
                "url": "",
            },
            "voted": {"icon": "", "color": "default", "url": "", "date": None},
        },
    ),
]
