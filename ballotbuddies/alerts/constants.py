from django.conf import settings

BASE_URL = settings.BASE_URL
if "localhost" in BASE_URL:
    BASE_URL = "https://app.michiganelections.io"

DEFAULT_ACTIVITY = ["Jace Browning is planning to vote"]

TEST_EMAIL_SUFFIX = " [TEST EMAIL]"
