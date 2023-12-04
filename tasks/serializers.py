from rest_framework import serializers

from .models import Task, TaskComment
from accounts.serializers import UserSerializer
from utils.fields import PassedTimeField


class TaskCommentSerializer(serializers.ModelSerializer):
    """
    Represent and serialise TaskComment model
    here is not extra functionality added
    """

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
    """
    list serialiser to Task model
    """

    created_at = serializers.DateTimeField(read_only=True)
    workgroup_name = serializers.CharField(source="workgroup.name", read_only=True)

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


class TaskDetailSerializer(TaskListSerializer):
    """
    Detail serializer to Task model, include related comments and workgroup
    """

    comments = TaskCommentSerializer(many=True, read_only=True)
    workgroup_name = serializers.CharField(source="workgroup.name", read_only=True)

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
        representation: dict = super().to_representation(instance)
        flat_comments = representation.get("comments", [])
        flat_comments.sort(
            key=lambda x: (-1 if x["answer_to"] is None else x["answer_to"])
        )
        print(flat_comments)
        proxy_ids = {}
        out_comments = {
            comment["id"]: comment
            for comment in flat_comments
            if comment["answer_to"] is None
        }
        for comment in flat_comments:
            if comment["answer_to"] is None:
                continue
            if comment["answer_to"] in out_comments:
                out_comments[comment["answer_to"]].setdefault("subcomments", []).append(
                    comment
                )
                proxy_ids[comment["id"]] = comment["answer_to"]
            else:
                out_comments[proxy_ids[comment["answer_to"]]].setdefault(
                    "subcomments", []
                ).append(comment)
                proxy_ids[comment["id"]] = proxy_ids[comment["answer_to"]]
        representation["comments"] = flat_comments

        # add workers full data to representation
        # (including UserSerializer in class prevernt add workers by pk)
        workers = UserSerializer(instance.workers.all(), many=True).data
        representation["workers"] = workers
        return representation
