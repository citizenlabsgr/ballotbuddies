from django.conf import settings

from .helpers import allow_debug


def debug(request):
    return {
        "debug": allow_debug(request),
        "debug_nav": settings.ALLOW_DEBUG,
    }
