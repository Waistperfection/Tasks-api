from django.urls import path
from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register(r"tasks", views.TaskViewSet, basename="tasks")
router.register(r"workgroups", views.WorkgroupViewSet, basename="workgroups")
router.register(r"invites", views.InviteViewSet, basename="invites")

urlpatterns = [
    path(
        "tasks/<int:task_id>/comments/",
        views.TaskCommentView.as_view(),
    ),  # create Comment
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        views.TaskCommentView.as_view(),
    ),  # retrieve, update, delete Comment
    # path("workgroups/", views.WorkgroupListAPIView.as_view()),
    path("free-workers/", views.FreeWorkersListApiView.as_view()),
]

urlpatterns.extend(router.urls)

# print(*router.urls, sep = "\n\n")
