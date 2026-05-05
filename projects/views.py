from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from users.forms import ProjectForm

from .models import Project


def root_redirect_view(request):
    return redirect("projects:list")


def projects_list_view(request):
    projects = Project.objects.select_related("owner").prefetch_related("participants").order_by("-created_at")
    paginator = Paginator(projects, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
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
    projects = request.user.favorites.select_related("owner").prefetch_related("participants").order_by("-created_at")
    return render(request, "projects/favorite_projects.html", {"projects": projects})


def project_details_view(request, project_id):
    project = get_object_or_404(Project.objects.select_related("owner").prefetch_related("participants"), pk=project_id)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm(initial={"status": Project.STATUS_OPEN})
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return redirect("projects:detail", project_id=project.id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            updated = form.save()
            return redirect("projects:detail", project_id=updated.id)
    else:
        form = ProjectForm(instance=project)

    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def toggle_favorite_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.user.favorites.filter(pk=project.pk).exists():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id == request.user.id:
        return JsonResponse({"status": "error", "message": "Owner cannot toggle participation"}, status=400)
    if project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error", "message": "Project is closed"}, status=400)

    if project.participants.filter(pk=request.user.id).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True

    return JsonResponse({"status": "ok", "participant": participant})


@login_required
@require_POST
def complete_project_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id or project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=403)

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": Project.STATUS_CLOSED})
