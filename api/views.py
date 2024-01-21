from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q, F, Prefetch
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from . import serializers
from .permissions import GroupTaskPermission, OnlyMasterPermission
from accounts.models import GroupInvite, Workgroup, User
from tasks.models import Task, TaskComment

from api import permissions

User = get_user_model()


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
        return Response({"message": message}, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=True, url_path="approve")
    def approve(self, request, pk=None):
        task = self.get_object()
        task.approved = True
        task.end_time = timezone.now()
        task.save()
        return Response({"message": "approved"}, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == "list":
            # minimal data on "list" method
            serializer_class = serializers.TaskListSerializer
        elif self.action in (
            "create",
            "update",
        ):
            serializer_class = serializers.TaskSerializer
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
    permission_classes = [
        IsAuthenticated,
    ]

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


# TODO: update queries in viewsets!!! too much duplication
class WorkgroupViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.WorkgroupSerializer
    permission_classes = [
        IsAuthenticated,
        GroupTaskPermission,
    ]
    lookup_field = "pk"

    @action(
        methods=["post"],
        detail=True,
        permission_classes=[
            OnlyMasterPermission,
        ],
    )
    def add(self, request, pk):
        # data {user_id} permission - workgroup owner
        # result - new inite to user with invite link
        # send email to user
        # chrck user is master>>get data>>get user or 404>>get workgroup>>check owner>>create invite link>>
        # >>send link to email

        workgroup = self.get_object()
        invite = serializers.WorkgroupInviteAddSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        print(invite.is_valid(raise_exception=True))
        print(invite.validated_data)
        invite.save()
        return Response({"data": invite.data}, status=status.HTTP_200_OK)

    @action(methods=["post", "delete"], detail=False)
    def join(self, request):
        # join to workgroup for non_moaster users
        if request.method == "POST":
            ...

    def get_queryset(self):
        prefetch_query = User.objects.all().only(
            "id", "first_name", "last_name", "username", "workgroup_id"
        )
        queryset = (
            Workgroup.objects.select_related("owner")
            .prefetch_related(Prefetch("workers", queryset=prefetch_query))
            .distinct()
            .all()
        )
        if self.request.user.is_master or self.request.user.workgroup:
            queryset = queryset.filter(
                Q(owner=self.request.user) | Q(workers__id=self.request.user.id)
            )  # type:ignore
        return queryset

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return serializers.WorkgroupSerializer
        elif self.action == "add":
            return serializers.WorkgroupInviteAddSerializer
        return serializers.WorkgroupListSerializer


class InviteViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    model = GroupInvite
    # serializer_class = serializers.WorkgroupInviteSerializer
    # queryset = GroupInvite.objects.all()
    lookup_field = "code"
    permission_classes = [
        permissions.permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = GroupInvite.objects.select_related("workgroup")
        if user.is_master:
            queryset = queryset.filter(workgroup__owner_id=user.id)
        else:
            queryset = queryset.filter(user_id=user.id)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.WorkgroupInviteListSerializer
        return serializers.WorkgroupInviteAddSerializer

    @action(
        methods=["get"],
        detail=True,
    )
    def accept(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if instance.user != user:
            return Response(
                {"message": "not yours invite code"}, status=status.HTTP_403_FORBIDDEN
            )
        user.workgroup = instance.workgroup
        user.save()
        return Response({"message": "success, you're added to group %s"}, status=status.HTTP_202_ACCEPTED)


class FreeWorkersListApiView(generics.ListAPIView):
    queryset = User.objects.filter(workgroup=None, is_master=False)
    serializer_class = serializers.UserSerializer
