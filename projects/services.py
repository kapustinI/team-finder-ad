from django.core.paginator import Paginator

from projects.constants import PROJECTS_PAGE_SIZE
from projects.models import Project


def get_project_queryset(queryset=None):
    base_queryset = queryset if queryset is not None else Project.objects
    return (
        base_queryset.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )


def paginate_queryset(request, queryset, page_size=PROJECTS_PAGE_SIZE):
    paginator = Paginator(queryset, page_size)
    return paginator.get_page(request.GET.get("page"))
