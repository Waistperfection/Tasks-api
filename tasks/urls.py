from django.urls import path, include

# from .views import TaskListView
from .views import router
from . import views


urlpatterns = [
    path(
        "", include(router.urls)
    ),  # task router includes list, retrive, create, update, delete
    path(
        "tasks/<int:task_id>/comments/",
        views.TaskCommentView.as_view(),
    ),  # create Comment
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        views.TaskCommentView.as_view(),
    ),  # retrive, update, delete Comment
]
