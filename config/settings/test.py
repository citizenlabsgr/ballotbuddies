from .default import *

# mypy: ignore-errors

# BASE_NAME and BASE_DOMAIN are intentionally unset
# None of the commands that rely on these values should run during tests
BASE_URL = "http://example.com"

ALLOW_DEBUG = True


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

MIDDLEWARE.remove("bugsnag.django.middleware.BugsnagMiddleware")
