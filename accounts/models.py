from ntpath import realpath
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_master = models.BooleanField("мастер?", default=False)
    workgroup = models.ForeignKey(
        "accounts.Workgroup",
        null=True,
        related_name="workers",
        on_delete=models.SET_NULL,
        blank=True,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользоватеworkли"

    def __str__(self):
        return self.username


class Workgroup(models.Model):
    name = models.CharField(max_length=150, unique=True)
    owner = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, related_name="workgroups", null=True
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.name


class GroupInvite(models.Model):
    workgroup = models.ForeignKey(
        Workgroup, related_name="group_invites", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    code = models.UUIDField(default=uuid.uuid4)

    class Meta:
        ...

    def __str__(self):
        return f"{self.workgroup.name}:{self.user.username}"


class GroupJoin(models.Model):
    workgroup = models.ForeignKey(
        Workgroup, on_delete=models.CASCADE, related_name="joins"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="joins")

    class Meta:
        ...

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.refresh_from_db()
        GroupJoin.objects.all().filter(user_id=self.user.id).exclude(
            pk=self.pk
        ).delete()
        print("all other deleted")
