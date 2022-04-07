from django.conf import settings
from django.contrib import admin
from django.urls import include, path

import debug_toolbar

urlpatterns = [
    path("", include("ballotbuddies.buddies.urls", namespace="buddies")),
    path("admin/", admin.site.urls),
    path("grappelli/", include("grappelli.urls")),
]

if settings.ALLOW_DEBUG:
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
        path("__reload__/", include("django_browser_reload.urls")),
    ] + urlpatterns
