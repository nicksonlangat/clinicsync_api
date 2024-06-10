from http import HTTPStatus

from django.urls import reverse

from accounts.models import PasswordResetToken

from .base_test import BaseTest


class UserAccountTests(BaseTest):
    def test_register_with_no_data(self) -> None:
        res = self.client.post(self.register_url)
        self.assertEqual(res.status_code, 400)

    def test_register_with_data(self) -> None:
        res = self.client.post(self.register_url, self.new_user)
        self.assertEqual(res.status_code, 201)

    def test_user_cannot_login_with_invalid_credentials(self):
        url = reverse("login")
        self.credentials["password"] = "1234"
        response = self.client.post(url, self.credentials, follow=True)
        self.assertEqual(response.status_code, 401)

    def test_login(self):
        url = reverse("login")
        response = self.client.post(url, self.credentials, follow=True)
        assert response.status_code == HTTPStatus.OK
        assert "access" in response.json()

    def test_password_reset(self):
        url = reverse("password-reset")
        payload = {"email": self.user.email, "action": "reset"}
        response = self.client.post(url, payload, follow=True)
        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        assert response_data["success"]

    def test_valid_password_reset_token(self):
        url = reverse("code-verify")
        token, created = PasswordResetToken.objects.get_or_create(user=self.user)
        payload = {"email": self.user.email, "code": token.code}
        response = self.client.post(url, payload, follow=True)
        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        assert response_data["success"]

    def test_invalid_password_reset_token(self):
        url = reverse("code-verify")
        token = 56765456
        payload = {"email": self.user.email, "code": token}
        response = self.client.post(url, payload, follow=True)
        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        self.assertFalse(response_data["success"])

    def test_activate_account_with_valid_code(self):
        url = reverse("activate-account")
        token, created = PasswordResetToken.objects.get_or_create(user=self.user)
        payload = {"email": self.user.email, "code": token.code}

        response = self.client.post(url, payload, follow=True)
        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        assert response_data["success"]

    def test_activate_account_with_invalid_code(self):
        url = reverse("activate-account")
        token = 7654567
        payload = {"email": self.user.email, "code": token}
        response = self.client.post(url, payload, follow=True)
        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        self.assertFalse(response_data["success"])

    def test_user_set_new_password(self):
        url = reverse("password-new")
        password = "7654efgfr5654ert"
        payload = {"email": self.user.email, "password": password}
        response = self.client.post(url, payload, follow=True)
        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        assert response_data["success"]
