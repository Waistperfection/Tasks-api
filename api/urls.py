from django.urls import path, include
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r"tasks", views.TaskViewSet, basename="tasks")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "tasks/<int:task_id>/comments/",
        views.TaskCommentView.as_view(),
    ),  # create Comment
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        views.TaskCommentView.as_view(),
    ),  # retrieve, update, delete Comment
    path("workgroups/", views.WorkgroupListAPIView.as_view()),
]
