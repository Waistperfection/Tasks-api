from rest_framework import generics, permissions
from django.db.models import Q

from . import serializers
from .models import Workgroup


# TODO: refactor, this is the part of accounts
class WorkgroupListAPIView(generics.ListAPIView):
    serializer_class = serializers.WorkgroupSerializer
    queryset = Workgroup.objects.prefetch_related("workers")
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = (
            Workgroup.objects.prefetch_related("workers")
            .filter(Q(owner=self.request.user) | Q(workers__id=self.request.user.id))
            .distinct()
            .all()
        )
        return queryset
