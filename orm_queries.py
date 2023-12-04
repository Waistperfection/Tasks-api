from django.db.models.functions import RowNumber
from django.db.models import Window, F

from tasks.models import Task

# Запрос с применением оконной функции row_number которая нумерует строки
# сгруппированные по признаку partition_by
# отсортированные по полю order_by(как ни странно)
# и фильтрует только первые 5 в каждой группе
qs = (
    Task.objects.all()
    .filter(workgroup__owner_id=3)
    .select_related("workgroup")
    .values("id", "title", "workgroup__name")
    .annotate(
        row_count=Window(
            expression=RowNumber(),
            partition_by=[
                F("workgroup__name"),
            ],
            order_by=[F("title")],
        )
    )
    .filter(row_count__lte=5)
)
