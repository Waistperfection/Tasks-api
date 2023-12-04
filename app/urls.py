from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView
from app import settings


urlpatterns = [
    path("", RedirectView.as_view(url="api/v1/tasks/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/v1/drf_auth/", include("rest_framework.urls")),
    re_path(r"^auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
    path("api/v1/", include("api.urls")),
]


if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
