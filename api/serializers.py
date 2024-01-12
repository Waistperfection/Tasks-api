import uuid
from rest_framework import serializers
from django.contrib.auth import get_user_model

from tasks.models import Task, TaskComment
from accounts.models import GroupInvite, Workgroup
from utils.fields import PassedTimeField
from .utils import build_related_comments_struct

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "workgroup",
        )

    def save(self, **kwargs):
        raise NotImplementedError


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "is_master",
            "workgroup_id",
        )


class WorkgroupSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Workgroup
        fields = (
            "id",
            "name",
            "owner",
            "workers",
        )
        extra_kwargs = {"workers": {"required": False}}


class WorkgroupListSerializer(WorkgroupSerializer):
    workers = UserSerializer(read_only=True, many=True)
    owner = UserSerializer()

    class Meta:
        model = Workgroup
        fields = (
            "id",
            "name",
            "owner",
            "workers",
        )


class WorkgroupDetailsSerializer(WorkgroupSerializer):
    ...


class TaskCommentSerializer(serializers.ModelSerializer):
    added = PassedTimeField(read_only=True)

    class Meta:
        model = TaskComment
        fields = (
            "id",
            "body",
            "task",
            "sender",
            "answer_to",
            "added",
        )
        read_only_fields = (
            "id",
            "sender",
            "task",
            "added",
        )


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title", "workgroup", "content", "workers")


class TaskListSerializer(TaskSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    workgroup_name = serializers.CharField(source="workgroup.name", read_only=True)
    workers = UserSerializer(many=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "content",
            "workgroup",
            "workgroup_name",
            "created_at",
            "workers",
        )
        read_only_fields = ("id", "title", "content", "created_at")


class TaskDetailSerializer(TaskListSerializer):
    workers = UserSerializer(many=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    workgroup = serializers.PrimaryKeyRelatedField(read_only=True)
    workgroup_name = serializers.CharField(source="workgroup.name")

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "content",
            "start_time",
            "end_time",
            "completed",
            "approved",
            "workgroup",
            "workgroup_name",
            "workers",
            "comments",
        )

        allow_empty = ("workers",)
        read_only_fields = (
            "id",
            "end_time",
            "completed",
            "approved",
            "comments",
        )

    # ONLY ONE LEVEL NESTED COMMENTS
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        flat_comments = representation.get("comments", [])
        representation["comments"] = build_related_comments_struct(flat_comments)

        return representation

    def validate(self, attrs):
        user = self.context["request"].user
        workgroup = attrs["workgroup"]
        workers = attrs["workers"]
        if user is not workgroup.owner:
            raise serializers.ValidationError("You can add tasks only in your groups")
        elif not set(workers).issubset(set(workgroup.workers.all())):
            raise serializers.ValidationError(
                "You can add only related with workgroup workers"
            )
        return super().validate(attrs)


class WorkgroupInviteAddSerializer(serializers.ModelSerializer):
    code = serializers.UUIDField(default=uuid.uuid4, read_only=True)

    class Meta:
        model = GroupInvite
        fields = (
            "code",
            "user",
            "workgroup",
        )

    def validate_user(self, user):
        if not (user.workgroup is None):
            raise serializers.ValidationError("You can add only free users")
        return user

    def validate_workgroup(self, workgroup):
        user = self.context["request"].user
        if not (user == workgroup.owner):
            raise serializers.ValidationError("You cant add users in this group")
        return workgroup


class WorkgroupInviteListSerializer(WorkgroupInviteAddSerializer):
    user = UserSerializer()
    workgroup = serializers.CharField(source="workgroup.name")

    class Meta:
        model = GroupInvite
        fields = (
            "id",
            "code",
            "user",
            "workgroup",
        )
