from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

import debug_toolbar

from ballotbuddies.core.views import zapier

urlpatterns: list = [
    path("", include("ballotbuddies.core.urls")),
    path("", include("ballotbuddies.friends.urls")),
    path("explore/", include("ballotbuddies.explore.urls")),
    path("zapier/", zapier),
    path("api/", include("ballotbuddies.api.urls")),
    path("admin/", admin.site.urls),
    path(
        "service-worker.js",
        (
            TemplateView.as_view(
                template_name="service-worker.js",
                content_type="application/javascript",
            )
        ),
        name="service-worker.js",
    ),
]

if settings.ALLOW_DEBUG:
    urlpatterns = [
        path("debug/", include("ballotbuddies.alerts.urls", namespace="alerts")),
        path("__debug__/", include(debug_toolbar.urls)),
        path("__reload__/", include("django_browser_reload.urls")),
    ] + urlpatterns
