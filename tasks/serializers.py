from rest_framework import serializers
from rest_framework.fields import empty

from pprint import pprint


from accounts.models import User, Workgroup
from .models import Task, TaskComment
from accounts.serializers import WorkgroupSerializer, UserSerializer


class FormattedDateTimeField(serializers.DateTimeField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # super().__init__(format="%d-%b-%Y %H:%M:%S", **kwargs)


class TaskCommentSerializer(serializers.ModelSerializer):
    """
    class to represent and serialise TaskComment model
    here is not extra functionality added
    """

    added = FormattedDateTimeField(read_only=True)

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
    created_at = FormattedDateTimeField(read_only=True)
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


# Full info about the task, include comments
class TaskDetailSerializer(TaskListSerializer):
    comments = TaskCommentSerializer(many=True, read_only=True)
    workgroup_name = serializers.CharField(source="workgroup.name", read_only=True)
    # workers = UserSerializer(many=True, read_only=True)

    # def validate_workers(data):
    #     print(data)
    #     return True

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

    # update comments representation from flat list to nested structure
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        comments_arr = representation.get("comments", [])
        comments = {comment["id"]: comment for comment in comments_arr}
        # create nested dict of comments
        for comment in comments_arr:
            if comment["answer_to"] is None:
                continue
            comments[comment["answer_to"]].setdefault("subcomments", []).append(comment)

        # filter only root comments
        representation["comments"] = [
            comment for comment in comments.values() if comment["answer_to"] is None
        ]
        # add workers full data to representation (including UserSerializer in class prevernt add workers by pk)
        workers = UserSerializer(instance.workers.all(), many=True).data
        representation["workers"] = workers
        return representation

    def get_workers(self, object):
        print("get.workers")


"""
TaskDetailSerializer():
    workgroup = PrimaryKeyRelatedField(label='Группа', queryset=Workgroup.objects.all())       
    id = IntegerField(label='ID', read_only=True)
    title = CharField(max_length=200)
    content = CharField(style={'base_template': 'textarea.html'})
    start_time = DateTimeField(allow_null=True, label='Старт', required=False)
    end_time = DateTimeField(allow_null=True, label='Окончание', read_only=True)
    completed = BooleanField(label='Завершено', read_only=True)
    approved = BooleanField(label='Утверждено', read_only=True)
    workers = PrimaryKeyRelatedField(allow_empty=False, many=True, queryset=User.objects.all())
    comments = TaskCommentSerializer(many=True, read_only=True):
        id = IntegerField(label='ID', read_only=True)
        body = CharField(label='Содержание', style={'base_template': 'textarea.html'})
        task = PrimaryKeyRelatedField(read_only=True)
        sender = PrimaryKeyRelatedField(read_only=True)
        answer_to = PrimaryKeyRelatedField(allow_null=True, queryset=TaskComment.objects.all(), required=False)
        added = DateTimeField(format='%d-%b-%Y %H:%M:%S', read_only=True)
"""
