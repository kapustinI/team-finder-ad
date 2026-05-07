from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from projects.constants import PROJECTS_PAGE_SIZE
from projects.forms import ProjectForm
from projects.models import Project
from projects.services import get_project_queryset, paginate_queryset


def root_redirect_view(request):
    return redirect("projects:list")


def projects_list_view(request):
    projects = get_project_queryset()
    page_obj = paginate_queryset(request, projects, PROJECTS_PAGE_SIZE)
    return render(
        request,
        "projects/project_list.html",
        {
            "projects": projects,
            "page_obj": page_obj,
            "query_prefix": "",
        },
    )


@login_required
def favorites_view(request):
    projects = get_project_queryset(request.user.favorites)
    return render(request, "projects/favorite_projects.html", {"projects": projects})


def project_details_view(request, project_id):
    project = get_object_or_404(get_project_queryset(), pk=project_id)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project_view(request):
    form = ProjectForm(request.POST or None, initial={"status": Project.STATUS_OPEN})
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:detail", project_id=project.id)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return redirect("projects:detail", project_id=project.id)

    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        updated = form.save()
        return redirect("projects:detail", project_id=updated.id)

    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def toggle_favorite_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if favorited := request.user.favorites.filter(pk=project.pk).exists():
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorited": not favorited})


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id == request.user.id:
        return JsonResponse(
            {"status": "error", "message": "Owner cannot toggle participation"},
            status=HTTPStatus.BAD_REQUEST,
        )
    if project.status != Project.STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "message": "Project is closed"},
            status=HTTPStatus.BAD_REQUEST,
        )

    if participant := project.participants.filter(pk=request.user.id).exists():
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse({"status": "ok", "participant": not participant})


@login_required
@require_POST
def complete_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id or project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": Project.STATUS_CLOSED})
