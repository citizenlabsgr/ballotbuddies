import os
from datetime import timedelta

from django.contrib import messages

import grappelli

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(CONFIG_ROOT)

LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

ALLOW_DEBUG = False

###############################################################################
# Core

INSTALLED_APPS = [
    "grappelli",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "corsheaders",
    "crispy_forms",
    "crispy_bootstrap5",
    "multi_email_field",
    "ballotbuddies.core",
    "ballotbuddies.buddies",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "sesame.middleware.AuthenticationMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "ballotbuddies": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

SITE_ID = 1

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

###############################################################################
# Sessions

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 52

###############################################################################
# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "US/Michigan"

USE_I18N = True

USE_L10N = True

USE_TZ = True

###############################################################################
# Static files

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(PROJECT_ROOT, "staticfiles")

###############################################################################
# CORS

CORS_ORIGIN_ALLOW_ALL = True

###############################################################################
# Grappelli

GRAPPELLI_ADMIN_TITLE = "Ballot Buddies Admin"

del grappelli.default_app_config  # fixes RemovedInDjango41Warning

###############################################################################
# Django Debug Toolbar

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_COLLAPSED": True,
    "SHOW_TOOLBAR_CALLBACK": "ballotbuddies.core.helpers.allow_debug",
}

###############################################################################
# Bootstrap

MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

###############################################################################
# Email

EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = os.getenv("SENDGRID_USERNAME")
EMAIL_HOST_PASSWORD = os.getenv("SENDGRID_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True

###############################################################################
# Django Sesame

SESAME_TOKEN_NAME = "token"
SESAME_MAX_AGE = timedelta(days=30)

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "sesame.backends.ModelBackend",
]

###############################################################################
# Michigan Elections

MICHIGAN_ELECTIONS_API = "https://michiganelections.io/api/status/"
