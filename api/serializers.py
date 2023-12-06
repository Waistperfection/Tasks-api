from rest_framework import serializers

from tasks.models import Task, TaskComment
from accounts.models import User, Workgroup
from utils.fields import PassedTimeField
from .utils import build_related_comments_struct


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
        )

    def save(self, **kwargs):
        raise NotImplementedError


class WorkgroupSerializer(serializers.ModelSerializer):
    workers = UserSerializer(read_only=True, many=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Workgroup
        fields = (
            "id",
            "name",
            "owner",
            "workers",
        )


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


class TaskListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    workgroup_name = serializers.CharField(source="workgroup.name", read_only=True)
    workers = UserSerializer(many=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "content",
            "workgroup_id",
            "workgroup_name",
            "created_at",
            "workers",
        )
        read_only_fields = ("id", "title", "content", "created_at")


class TaskDetailSerializer(serializers.ModelSerializer):
    workers = UserSerializer(many=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    workgroup_id = serializers.IntegerField()
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
            "workgroup_id",
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
            raise serializers.ValidationError('You can add tasks only in your groups')
        elif not set(workers).issubset(set(workgroup.workers.all())):
            raise serializers.ValidationError('You can add only related with workgroup workers')
        return super().validate(attrs)
