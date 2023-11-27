from rest_framework import serializers

from .models import User, Workgroup


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "is_master",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
        )


class WorkgroupSerializer(serializers.ModelSerializer):
    workers = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Workgroup
        fields = (
            "id",
            "name",
            "workers",
        )
