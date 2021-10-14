from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('', include('ballotbuddies.buddies.urls', namespace='buddies')),
    path('api/', include('ballotbuddies.api.urls')),

    path('admin/', admin.site.urls),
    path('grappelli/', include('grappelli.urls')),
]
