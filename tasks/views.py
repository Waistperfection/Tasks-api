from pprint import pprint
from typing import Any
from django import http
from rest_framework import viewsets
from rest_framework import generics
from rest_framework import routers
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from django.utils import timezone
from .permissions import TaskPermission

from .serializers import TaskListSerializer, TaskDetailSerializer, TaskCommentSerializer
from .models import Task, TaskComment
from accounts.models import User

# router = routers.SimpleRouter()
router = routers.DefaultRouter()


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskListSerializer
    # TODO don't forget uncomment permissions!!!
    permission_classes = (TaskPermission,)

    @action(methods=["get"], detail=True, url_path="complete")
    def complete(self, request, pk=None):
        task = self.get_object()
        task.competed = True
        task.save()
        return Response({"messsage": "completed"}, status=200)

    @action(methods=["get"], detail=True, url_path="approve")
    def approve(self, request, pk=None):
        task = self.get_object()
        task.end_time = timezone.now()
        task.save()
        return Response({"messsage": "approved"}, status=200)

    def get_serializer_class(self):
        if self.action == "list":
            serializer_class = TaskListSerializer
        else:
            serializer_class = TaskDetailSerializer
        # print(repr(serializer_class))
        return serializer_class

    def get_queryset(self):
        # get base queryset
        queryset = Task.objects.select_related("workgroup").prefetch_related("workers")
        # if user.is_master return tasks for all master workgroups
        # master can have more than one workgroup
        if self.request.user.is_master:
            queryset = queryset.filter(
                Q(workgroup__owner_id=self.request.user.id)
                | Q(workgroup__id=self.request.user.workgroup_id)
            )
        # else if user is worker return task
        # worker can have only one workgroup
        else:
            queryset = Task.objects.filter(workers=self.request.user)
        # if get return detail view of task we wanna add some extra objects to serializer
        # like recursive comments
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("comments")
        queryset = queryset.order_by("workgroup", "-created_at")
        return queryset

    def perform_create(self, serializer):
        # workers = User.objects.all().filter(pk__in=self.request.data.get("workers", []))
        # print(workers)
        return super().perform_create(serializer)


class TaskCommentView(
    generics.mixins.CreateModelMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = TaskCommentSerializer
    lookup_url_kwarg = "comment_id"

    def setup(self, request, *args: Any, **kwargs: Any) -> None:
        return super().setup(request, *args, **kwargs)
    
    # def post(self, *args, **kwargs):
    #     return self.create(*args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(
            task_id=self.kwargs["task_id"], sender_id=self.request.user.id
        )

    def get_queryset(self):
        queryset = TaskComment.objects.filter(
            task_id=self.kwargs["task_id"]
        ).select_related("sender")
        return queryset


# TODO: refactor to the api.py file in app module
router.register(r"tasks", TaskViewSet, basename="tasks")
