from django.urls import path, include

from . import views


urlpatterns = [
    path("workgroups/", views.WorkgroupListAPIView.as_view()),
]
