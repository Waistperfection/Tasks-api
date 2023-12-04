from django.urls import path
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r"tasks", views.TaskViewSet, basename="tasks")


urlpatterns = [
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

urlpatterns.extend(router.urls)
