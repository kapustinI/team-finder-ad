from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Project


User = get_user_model()


class ProjectsFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            email="owner@example.com",
            password="OwnerPass123!",
            name="Owner",
            surname="User",
        )
        cls.member = User.objects.create_user(
            email="member@example.com",
            password="MemberPass123!",
            name="Member",
            surname="User",
        )
        cls.project = Project.objects.create(
            name="Test Project",
            description="Description",
            owner=cls.owner,
            status=Project.STATUS_OPEN,
        )
        cls.project.participants.add(cls.owner)

        cls.owner_client = Client()
        cls.owner_client.force_login(cls.owner)
        cls.member_client = Client()
        cls.member_client.force_login(cls.member)

    def test_create_project_requires_auth(self):
        response = self.client.get(reverse("projects:create"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("users:login"), response.url)

    def test_authenticated_user_creates_project_and_becomes_participant(self):
        response = self.member_client.post(
            reverse("projects:create"),
            {
                "name": "New Project",
                "description": "Some text",
                "github_url": "https://github.com/example/new-project",
                "status": Project.STATUS_OPEN,
            },
        )

        created = Project.objects.get(name="New Project")
        self.assertRedirects(
            response,
            reverse("projects:detail", kwargs={"project_id": created.id}),
        )
        self.assertEqual(created.owner, self.member)
        self.assertTrue(created.participants.filter(id=self.member.id).exists())

    def test_toggle_favorite_requires_auth(self):
        response = self.client.post(
            reverse(
                "projects:toggle_favorite",
                kwargs={"project_id": self.project.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_toggle_favorite_adds_and_removes_project(self):
        scenarios = [
            ("add", True),
            ("remove", False),
        ]
        for action, expected_exists in scenarios:
            with self.subTest(action=action):
                response = self.member_client.post(
                    reverse(
                        "projects:toggle_favorite",
                        kwargs={"project_id": self.project.id},
                    )
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertEqual(
                    self.member.favorites.filter(id=self.project.id).exists(),
                    expected_exists,
                )

    def test_only_owner_can_complete_project(self):
        forbidden = self.member_client.post(
            reverse("projects:complete", kwargs={"project_id": self.project.id})
        )
        self.assertEqual(forbidden.status_code, HTTPStatus.FORBIDDEN)

        ok = self.owner_client.post(
            reverse("projects:complete", kwargs={"project_id": self.project.id})
        )
        self.assertEqual(ok.status_code, HTTPStatus.OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.STATUS_CLOSED)

    def test_cannot_participate_in_closed_project(self):
        self.project.status = Project.STATUS_CLOSED
        self.project.save(update_fields=["status"])

        response = self.member_client.post(
            reverse(
                "projects:toggle_participate",
                kwargs={"project_id": self.project.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertFalse(self.project.participants.filter(id=self.member.id).exists())

    def test_open_project_participation_toggles_for_non_owner(self):
        join_response = self.member_client.post(
            reverse(
                "projects:toggle_participate",
                kwargs={"project_id": self.project.id},
            )
        )
        self.assertEqual(join_response.status_code, HTTPStatus.OK)
        self.assertTrue(self.project.participants.filter(id=self.member.id).exists())

        leave_response = self.member_client.post(
            reverse(
                "projects:toggle_participate",
                kwargs={"project_id": self.project.id},
            )
        )
        self.assertEqual(leave_response.status_code, HTTPStatus.OK)
        self.assertFalse(self.project.participants.filter(id=self.member.id).exists())
