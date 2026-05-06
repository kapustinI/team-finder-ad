from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class AuthFlowTests(TestCase):
    def test_register_logs_in_and_redirects_to_projects_list(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "Ivan",
                "surname": "Tester",
                "email": "ivan_test@example.com",
                "password": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("projects:list"))
        self.assertTrue(User.objects.filter(email="ivan_test@example.com").exists())

        user = User.objects.get(email="ivan_test@example.com")
        session_user_id = self.client.session.get("_auth_user_id")
        self.assertEqual(str(user.id), str(session_user_id))

    def test_login_with_invalid_credentials_shows_error(self):
        User.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
            name="Name",
            surname="Surname",
        )

        response = self.client.post(
            reverse("users:login"),
            {
                "email": "user@example.com",
                "password": "wrong-pass",
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Неверный email или пароль")

    def test_participants_list_is_accessible_for_guest(self):
        response = self.client.get(reverse("users:list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
