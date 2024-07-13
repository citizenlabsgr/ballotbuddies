import random
import string

from django.conf import settings


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


def generate_key(length=8):
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def parse_domain(email: str) -> tuple[str, bool]:
    domain = email.split("@")[-1]
    standard = domain in {
        "aol.com",
        "comcast.net",
        "gmail.com",
        "hotmail.com",
        "icloud.com",
        "live.com",
        "mail.com",
        "msn.com",
        "outlook.com",
        "yahoo.com",
        "ymail.com",
    }
    return domain, standard
