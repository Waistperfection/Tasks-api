from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as StockUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Workgroup, Groupjoin


@admin.register(User)
class UserAdmin(StockUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_master",
    )

    fieldsets = fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (None, {"fields": ("is_master", "workgroup")}),
    )


@admin.register(Workgroup)
class WorkgroupAdmin(admin.ModelAdmin):
    ...


@admin.register(Groupjoin)
class GroupjoinAdmin(admin.ModelAdmin):
    ...
