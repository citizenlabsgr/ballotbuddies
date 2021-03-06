from django.conf import settings
from django.contrib import admin
from django.urls import include, path

import debug_toolbar

urlpatterns = [
    path("", include("ballotbuddies.buddies.urls", namespace="buddies")),
    path("api/", include("ballotbuddies.api.urls")),
    path("admin/", admin.site.urls),
]

if settings.ALLOW_DEBUG:
    urlpatterns = [
        path("emails/", include("ballotbuddies.alerts.urls", namespace="alerts")),
        path("__debug__/", include(debug_toolbar.urls)),
        path("__reload__/", include("django_browser_reload.urls")),
    ] + urlpatterns
