from django.conf import settings

if getattr(settings, "TEST", False):
    LIMIT = 20
else:
    LIMIT = 0
