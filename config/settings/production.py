import os
import urllib

import dj_database_url

from .default import *

BASE_NAME = os.environ["HEROKU_APP_NAME"]
BASE_DOMAIN = "app.michiganelections.io"
BASE_URL = f"https://{BASE_DOMAIN}"

if BASE_NAME == "local":
    ALLOW_DEBUG = True

###############################################################################
# Core

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = ["localhost", ".michiganelections.io"]

CSRF_TRUSTED_ORIGINS = ["https://*.michiganelections.io"]

###############################################################################
# Databases

DATABASES = {}
DATABASES["default"] = dj_database_url.config()

###############################################################################
# Caches

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ["REDIS_URL"],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
    "explore": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/tmp/django/explore",
        "TIMEOUT": 60 * 60 * 6,
    },
}

###############################################################################
# Authentication

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

###############################################################################
# Static files

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
