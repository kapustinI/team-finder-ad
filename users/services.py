from core.services import paginate_queryset


def apply_variant1_filter(request, queryset):
    active_filter = request.GET.get("filter", "")
    if not (active_filter and request.user.is_authenticated):
        return queryset, ""

    me = request.user
    if active_filter == "owners-of-favorite-projects":
        project_ids = me.favorites.values_list("id", flat=True)
        queryset = queryset.filter(owned_projects__id__in=project_ids)
    elif active_filter == "owners-of-participating-projects":
        project_ids = me.participated_projects.values_list("id", flat=True)
        queryset = queryset.filter(owned_projects__id__in=project_ids)
    elif active_filter == "interested-in-my-projects":
        my_project_ids = me.owned_projects.values_list("id", flat=True)
        queryset = queryset.filter(favorites__id__in=my_project_ids)
    elif active_filter == "participants-of-my-projects":
        my_project_ids = me.owned_projects.values_list("id", flat=True)
        queryset = queryset.filter(participated_projects__id__in=my_project_ids)
    else:
        active_filter = ""

    return queryset.distinct(), active_filter


def build_query_prefix(active_filter):
    query_parts = []
    if active_filter:
        query_parts.append(f"filter={active_filter}")
    query_prefix = "&".join(query_parts)
    if query_prefix:
        query_prefix += "&"
    return query_prefix
