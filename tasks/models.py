from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    workers = models.ManyToManyField("accounts.User")
    workgroup = models.ForeignKey(
        "accounts.Workgroup",
        verbose_name="Группа",
        related_name="tasks",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)
    start_time = models.DateTimeField("Старт", null=True, blank=True)
    end_time = models.DateTimeField("Окончание", null=True, blank=True)
    completed = models.BooleanField("Завершено", default=False)
    approved = models.BooleanField("Утверждено", default=False)

    class Meta:
        verbose_name = "Задачу"
        verbose_name_plural = "Задачи"

    def __str__(self):
        return self.title

    # def get_absolute_url(self):
    #     return reverse('_detail', kwargs={'pk': self.pk})


class TaskComment(models.Model):
    task = models.ForeignKey(
        "tasks.Task", related_name="comments", on_delete=models.CASCADE
    )
    body = models.TextField("содержание")
    sender = models.ForeignKey(
        "accounts.User", related_name="comments", on_delete=models.CASCADE
    )
    answer_to = models.ForeignKey(
        "tasks.TaskComment",
        related_name="subcomments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    added = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        verbose_name = "коментарий"
        verbose_name_plural = "коментарии"

    def __str__(self):
        return self.body

    # def get_absolute_url(self):
    #     return reverse('_detail', kwargs={'pk': self.pk})


def get_directory_path(instance, filename):
    if instance.task:
        root_folder, id = "tasks", instance.task.id
    else:
        root_folder, id = "comments", instance.comment.id
    return f"{root_folder}/{id}/{filename}"


class TaskImage(models.Model):
    task = models.ForeignKey(
        "tasks.Task",
        related_name="images",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    comment = models.ForeignKey(
        "tasks.TaskComment",
        related_name="images",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    image = models.ImageField(upload_to=get_directory_path)

    class Meta:
        verbose_name = "Картинка"
        verbose_name_plural = "Картинки"

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('Image_detail', kwargs={'pk': self.pk})
