# mypy: ignore-errors

from datetime import date

import bugsnag

from .production import *

BASE_NAME = os.environ["HEROKU_APP_NAME"]
if BASE_NAME.count("-") >= 2:
    BASE_DOMAIN = f"{BASE_NAME}.herokuapp.com"
    DEBUG = True
    TODAY = date(2021, 9, 15)
else:
    BASE_DOMAIN = "staging-app.michiganelections.io"
BASE_URL = f"https://{BASE_DOMAIN}"


ALLOW_DEBUG = True

###############################################################################
# Core

ALLOWED_HOSTS += [".herokuapp.com", ".michiganelections.io"]

###############################################################################
# Authentication

AUTH_PASSWORD_VALIDATORS = []

###############################################################################
# Bugsnag

bugsnag.configure(release_stage="staging")
