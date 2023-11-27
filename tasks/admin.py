from django.contrib import admin

from .models import Task, TaskComment, TaskImage


class TaskCommentInline(admin.TabularInline):
    model = TaskComment


class SubcommentsInlie(admin.TabularInline):
    model = TaskComment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "workgroup_name",
        "start_time",
        "completed",
        "approved",
    )
    inlines = [
        TaskCommentInline,
    ]

    @admin.display(description="Группа")
    def workgroup_name(self, obj):
        return obj.workgroup.name


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    inlines = [
        SubcommentsInlie,
    ]
    ...


@admin.register(TaskImage)
class TaskImageAdmin(admin.ModelAdmin):
    ...
