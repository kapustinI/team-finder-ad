from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, ProfileEditForm, RegisterForm, UserPasswordChangeForm
from .models import User


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:list")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            login(request, form.user)
            return redirect("projects:list")
    else:
        form = LoginForm(request=request)
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_details_view(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user, current_user=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = ProfileEditForm(instance=request.user, current_user=request.user)
    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:detail", user_id=request.user.id)
    else:
        form = UserPasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def _apply_variant1_filter(request, queryset):
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


def participants_list_view(request):
    participants = User.objects.all().order_by("id")
    participants, active_filter = _apply_variant1_filter(request, participants)

    paginator = Paginator(participants, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    query_parts = []
    if active_filter:
        query_parts.append(f"filter={active_filter}")
    query_prefix = "&".join(query_parts)
    if query_prefix:
        query_prefix += "&"

    return render(
        request,
        "users/participants.html",
        {
            "participants": participants,
            "page_obj": page_obj,
            "active_filter": active_filter,
            "query_prefix": query_prefix,
        },
    )
