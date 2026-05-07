from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from users.constants import USERS_PAGE_SIZE
from users.forms import LoginForm, ProfileEditForm, RegisterForm, UserPasswordChangeForm
from users.models import User
from users.services import apply_variant1_filter, build_query_prefix, paginate_queryset


def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("projects:list")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    form = LoginForm(request.POST or None, request=request)
    if form.is_valid():
        login(request, form.user)
        return redirect("projects:list")
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def user_details_view(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile_view(request):
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
        current_user=request.user,
    )
    if form.is_valid():
        form.save()
        return redirect("users:detail", user_id=request.user.id)
    return render(request, "users/edit_profile.html", {"form": form, "user": request.user})


@login_required
def change_password_view(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:detail", user_id=request.user.id)
    return render(request, "users/change_password.html", {"form": form})


def participants_list_view(request):
    participants = User.objects.all().order_by("id")
    participants, active_filter = apply_variant1_filter(request, participants)
    page_obj = paginate_queryset(request, participants, USERS_PAGE_SIZE)
    query_prefix = build_query_prefix(active_filter)

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
