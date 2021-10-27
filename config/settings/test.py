from datetime import date

import bugsnag

from .default import *

# mypy: ignore-errors


# BASE_NAME and BASE_DOMAIN are intentionally unset
# None of the commands that rely on these values should run during tests
BASE_URL = "http://example.com"

TODAY = date(2021, 10, 1)

###############################################################################
# Core

TEST = True
DEBUG = True
SECRET_KEY = "test"

LOGGING["loggers"]["ballotbuddies"]["level"] = "DEBUG"

###############################################################################
# Databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ballotbuddies_test",
        "HOST": "127.0.0.1",
    }
}

###############################################################################
# Bugsnag

bugsnag.configure(release_stage="test")
