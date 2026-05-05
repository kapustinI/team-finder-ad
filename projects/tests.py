from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Project


User = get_user_model()


class ProjectsFlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="OwnerPass123!",
            name="Owner",
            surname="User",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            password="MemberPass123!",
            name="Member",
            surname="User",
        )
        self.project = Project.objects.create(
            name="Test Project",
            description="Description",
            owner=self.owner,
            status=Project.STATUS_OPEN,
        )
        self.project.participants.add(self.owner)

    def test_create_project_requires_auth(self):
        response = self.client.get(reverse("projects:create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

    def test_authenticated_user_creates_project_and_becomes_participant(self):
        self.client.force_login(self.member)
        response = self.client.post(
            reverse("projects:create"),
            {
                "name": "New Project",
                "description": "Some text",
                "github_url": "https://github.com/example/new-project",
                "status": Project.STATUS_OPEN,
            },
        )

        created = Project.objects.get(name="New Project")
        self.assertRedirects(response, reverse("projects:detail", kwargs={"project_id": created.id}))
        self.assertEqual(created.owner, self.member)
        self.assertTrue(created.participants.filter(id=self.member.id).exists())

    def test_toggle_favorite_requires_auth(self):
        response = self.client.post(reverse("projects:toggle_favorite", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 302)

    def test_toggle_favorite_adds_and_removes_project(self):
        self.client.force_login(self.member)

        add_response = self.client.post(reverse("projects:toggle_favorite", kwargs={"project_id": self.project.id}))
        self.assertEqual(add_response.status_code, 200)
        self.assertTrue(self.member.favorites.filter(id=self.project.id).exists())

        remove_response = self.client.post(reverse("projects:toggle_favorite", kwargs={"project_id": self.project.id}))
        self.assertEqual(remove_response.status_code, 200)
        self.assertFalse(self.member.favorites.filter(id=self.project.id).exists())

    def test_only_owner_can_complete_project(self):
        self.client.force_login(self.member)
        forbidden = self.client.post(reverse("projects:complete", kwargs={"project_id": self.project.id}))
        self.assertEqual(forbidden.status_code, 403)

        self.client.force_login(self.owner)
        ok = self.client.post(reverse("projects:complete", kwargs={"project_id": self.project.id}))
        self.assertEqual(ok.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.STATUS_CLOSED)

    def test_cannot_participate_in_closed_project(self):
        self.project.status = Project.STATUS_CLOSED
        self.project.save(update_fields=["status"])

        self.client.force_login(self.member)
        response = self.client.post(reverse("projects:toggle_participate", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.project.participants.filter(id=self.member.id).exists())

    def test_open_project_participation_toggles_for_non_owner(self):
        self.client.force_login(self.member)

        join_response = self.client.post(reverse("projects:toggle_participate", kwargs={"project_id": self.project.id}))
        self.assertEqual(join_response.status_code, 200)
        self.assertTrue(self.project.participants.filter(id=self.member.id).exists())

        leave_response = self.client.post(reverse("projects:toggle_participate", kwargs={"project_id": self.project.id}))
        self.assertEqual(leave_response.status_code, 200)
        self.assertFalse(self.project.participants.filter(id=self.member.id).exists())
