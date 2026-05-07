from core.services import paginate_queryset
from projects.models import Project


def get_project_queryset(queryset=None):
    base_queryset = queryset or Project.objects
    return (
        base_queryset.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )
