from django.conf import settings
from django.db import models
from django.urls import reverse

from team_finder.constants import PROJECT_NAME_MAX_LENGTH


class Project(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_CLOSED, "Closed"),
    ]
    STATUS_MAX_LENGTH = max(len(status) for status, _ in STATUS_CHOICES)

    name = models.CharField(max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
    )

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"project_id": self.pk})
