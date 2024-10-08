import os
from datetime import timedelta

from django.contrib import messages

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(CONFIG_ROOT)

ALLOW_DEBUG = False

###############################################################################
# Core

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "debug_toolbar",
    "django_htmx",
    "django_user_agents",
    "corsheaders",
    "crispy_forms",
    "crispy_bootstrap5",
    "markdownify",
    "multi_email_field",
    "qr_code",
    "annoying",
    "rest_framework",
    "ballotbuddies.core",
    "ballotbuddies.api",
    "ballotbuddies.buddies",
    "ballotbuddies.alerts",
    "ballotbuddies.explore",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "bugsnag.django.middleware.BugsnagMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "sesame.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
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
                "ballotbuddies.core.context_processors.debug",
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
        "bugsnag": {
            "level": "CRITICAL",
            "class": "bugsnag.handlers.BugsnagHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "bugsnag"],
            "level": "INFO",
        },
        "ballotbuddies": {
            "handlers": ["console", "bugsnag"],
            "level": "DEBUG",
        },
    },
}

SITE_ID = 1

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

###############################################################################
# Caches

CACHES: dict = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "explore": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(os.getcwd(), ".cache/django/explore"),
    },
}

###############################################################################
# Sessions

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 52

###############################################################################
# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Detroit"

USE_I18N = True

USE_TZ = True

###############################################################################
# Static files

STATICFILES_DIRS = [os.path.join(PROJECT_ROOT, "static")]

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(PROJECT_ROOT, "staticfiles")

###############################################################################
# CORS

CORS_ORIGIN_ALLOW_ALL = True

###############################################################################
# Django Debug Toolbar

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_COLLAPSED": True,
    "SHOW_TOOLBAR_CALLBACK": "ballotbuddies.core.helpers.allow_debug",
}

###############################################################################
# Bootstrap

MESSAGE_TAGS = {
    messages.DEBUG: "alert-light",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

###############################################################################
# Markdownify

MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": ["p", "li", "ol", "ul"],
        "STRIP": False,
    }
}

###############################################################################
# Email

EMAIL = "Ballot Buddies <no-reply@michiganelections.io>"

EMAIL_HOST = "smtp.mandrillapp.com"
EMAIL_HOST_USER = "Citizen Labs"
EMAIL_HOST_PASSWORD = os.getenv("MANDRILL_API_KEY")
EMAIL_PORT = 587

###############################################################################
# Django Sesame

SESAME_TOKEN_NAME = "token"
SESAME_MAX_AGE = timedelta(days=30)

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "sesame.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

###############################################################################
# Django allauth

SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True

SOCIALACCOUNT_ADAPTER = "ballotbuddies.core.adapters.SocialAccountAdapter"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
            "secret": os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    }
}

GOOGLE_AUTH_ENABLED = (
    os.getenv("GOOGLE_OAUTH_CLIENT_ID") and os.getenv("GOOGLE_OAUTH_DISABLED") != "true"
)
