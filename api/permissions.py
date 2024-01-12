from rest_framework import permissions



class GroupTaskPermission(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        user = request.user
        if view.action == "create" and not user.is_master:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        # any related with task user can set it completed
        if view.action == "complete":
            return user in obj.workers
        # only group owner can approve, update or delete task
        elif view.action in (
            "approve",
            "update",
            "partial_update",
            "destroy",
        ):
            return user.is_master
        else:
            return True

class OnlyMasterPermission(permissions.IsAuthenticated):

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_master
