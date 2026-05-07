from django import forms

from core.mixins import GitHubURLValidationMixin
from projects.models import Project


class ProjectForm(GitHubURLValidationMixin, forms.ModelForm):
    status = forms.ChoiceField(
        choices=Project.STATUS_CHOICES,
        label="Статус",
    )

    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
