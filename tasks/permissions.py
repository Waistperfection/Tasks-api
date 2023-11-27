from rest_framework import permissions


# not seve menthods depricated for not author of object
class TaskPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if view.action == "create":
            return request.user.is_master
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if view.action == "complete":
            return request.user in obj.workers.all()
        elif view.action in (
            "approve",
            "update",
            "partial_update",
            "destroy",
        ):
            return request.user == obj.workgroup.owner

        else:
            return super().has_object_permission(request, view, obj)
