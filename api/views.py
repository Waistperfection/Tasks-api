from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated

from . import serializers
from .permissions import TaskPermission
from accounts.models import Workgroup
from tasks.models import Task, TaskComment


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TaskListSerializer
    permission_classes = (TaskPermission,)

    @action(methods=["post", "delete"], detail=True, url_path="complete")
    def complete(self, request, pk=None):
        task = self.get_object()
        if request.method == "POST":
            task.completed = True
        if request.method == "DELETE":
            task.completed = False
        task.save()
        message = "set completed" if task.completed else "set uncompleted"
        return Response({"message": message}, status=200)

    @action(methods=["post"], detail=True, url_path="approve")
    def approve(self, request, pk=None):
        task = self.get_object()
        task.approved = True
        task.end_time = timezone.now()
        task.save()
        return Response({"message": "approved"}, status=200)

    def get_serializer_class(self):
        if self.action == "list":
            # minimal data on "list" method
            serializer_class = serializers.TaskListSerializer
        else:
            # more data on detail methods
            serializer_class = serializers.TaskDetailSerializer
        return serializer_class

    def get_queryset(self):
        # get base queryset
        queryset = Task.objects.select_related("workgroup").prefetch_related("workers")
        # if user.is_master return tasks for all master workgroups
        # master can have more than one workgroup
        if self.request.user.is_master:  # type: ignore
            queryset = queryset.filter(
                Q(workgroup__owner_id=self.request.user.id)  # type: ignore
                | Q(workgroup__id=self.request.user.workgroup_id)  # type: ignore
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


class TaskCommentView(
    generics.mixins.CreateModelMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = serializers.TaskCommentSerializer
    lookup_url_kwarg = "comment_id"

    def post(self, *args, **kwargs):
        return self.create(*args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(
            task_id=self.kwargs["task_id"],
            sender_id=self.request.user.id,  # type:ignore
        )

    def get_queryset(self):
        queryset = TaskComment.objects.filter(
            task_id=self.kwargs["task_id"]
        ).select_related("sender")
        return queryset


class WorkgroupListAPIView(generics.ListAPIView):
    serializer_class = serializers.WorkgroupSerializer
    queryset = Workgroup.objects.prefetch_related("workers")
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            Workgroup.objects.prefetch_related("workers")
            .filter(Q(owner=self.request.user) | Q(workers__id=self.request.user.id))  # type:ignore
            .distinct()
            .all()
        )
        return queryset
