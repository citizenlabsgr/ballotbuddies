# TODO: Upgrade mypy to 0.991+ when django-stubs supports it
# mypy: ignore_errors

import random
import string
from datetime import date

from django.conf import settings
from django.utils import timezone


def today() -> date:
    return settings.TODAY or timezone.now().date()


def build_url(path: str) -> str:
    assert settings.BASE_URL
    assert path.startswith("/")
    return settings.BASE_URL + path


def allow_debug(request) -> bool:
    if not settings.ALLOW_DEBUG:
        return False
    if request.GET.get("debug") == "false":
        return False
    if request.GET.get("debug"):
        return True
    return settings.DEBUG


def generate_key(length=10):
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))
