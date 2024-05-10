# mypy: ignore-errors

import os
from datetime import date

import bugsnag
import dj_database_url

from .default import *

BASE_NAME = BASE_DOMAIN = "localhost"
BASE_URL = f"http://{BASE_DOMAIN}:8000"

ALLOW_DEBUG = True

###############################################################################
# Core

DEBUG = True
SECRET_KEY = "dev"

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".ngrok.io",
    ".ngrok.app",
]
INTERNAL_IPS = ALLOWED_HOSTS

INSTALLED_APPS += [
    "django_browser_reload",
]

MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

###############################################################################
# Databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "ballotbuddies_dev",
        "HOST": "127.0.0.1",
    }
}

if "DATABASE_URL" in os.environ:
    DATABASES["default"] = dj_database_url.config()

###############################################################################
# Caches

CACHES["explore"]["TIMEOUT"] = 60

###############################################################################
# Bootstrap

MESSAGE_LEVEL = messages.DEBUG

###############################################################################
# Bugsnag

if "BUGSNAG_API_KEY" in os.environ:
    bugsnag.configure(release_stage="local")
else:
    MIDDLEWARE.remove("bugsnag.django.middleware.BugsnagMiddleware")
