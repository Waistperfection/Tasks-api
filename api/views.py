from rest_framework import viewsets, mixins
from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Q, F, Prefetch
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated

from . import serializers
from .permissions import GroupTaskPermission
from accounts.models import Workgroup, User
from tasks.models import Task, TaskComment


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TaskListSerializer
    permission_classes = (
        IsAuthenticated,
        GroupTaskPermission,
    )

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
        user = self.request.user
        # get base queryset
        prefetch_query = User.objects.all().only(
            "id", "first_name", "last_name", "username"
        )
        queryset = Task.objects.select_related("workgroup").prefetch_related(
            Prefetch("workers", prefetch_query)
        )
        # If user.is_master return tasks for all master workgroups
        if user.is_master:  # type: ignore
            queryset = queryset.filter(
                Q(workgroup__owner_id=user.id)  # type: ignore
                | Q(workgroup__id=user.workgroup_id)  # type: ignore
            )
        # else if user is worker return tasks from his group
        else:
            # only user tasks
            # queryset = queryset.filter(workers=user.id)
            # all workgroup tasks
            queryset = queryset.filter(workgroup__id=user.workgroup_id)
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
    permission_classes = [IsAuthenticated,]

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


class WorkgroupViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.WorkgroupSerializer
    permission_classes = [
        IsAuthenticated,
        GroupTaskPermission,
    ]
    lookup_field = "pk"

    @action(methods=["post"], detail=False)
    def add(self, request):
        ...

    @action(methods=["get", "post", "delete"], detail=False)
    def join(self, request):
        if request.method == "GET":
            ...

    def get_queryset(self):
        prefetch_query = User.objects.all().only(
            "id", "first_name", "last_name", "username", "workgroup_id"
        )
        if self.action == "list":
            queryset = (
                Workgroup.objects
                .select_related('owner')
                .prefetch_related(Prefetch(
                    "workers", queryset=prefetch_query)
                )
                .filter(
                    Q(owner=self.request.user) | Q(workers__id=self.request.user.id)
                )  # type:ignore
                .distinct()
                .all()
            )
        else:
            queryset = Workgroup.objects.all()
        return queryset
