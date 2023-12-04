from rest_framework import permissions


class TaskPermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        user = request.user
        if view.action == "create":
            # only master can create tasks
            if not user.is_master:
                return False
            # master can create tasks only in his own groups
            workgroups_id_list = user.workgroups.all().values_list("id", flat=True)
            return request.data.get("workgroup") in workgroups_id_list
        print(view.action)
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        user = request.user
        # any related with task user can set it completed
        if view.action == "complete":
            return user in obj.workers.all()
        # only group owner can approve, update or delete task
        elif view.action in (
            "approve",
            "update",
            "partial_update",
            "destroy",
        ):
            return user == obj.workgroup.owner
        else:
            return user in obj.workers.all() or user == obj.workgroup.owner
