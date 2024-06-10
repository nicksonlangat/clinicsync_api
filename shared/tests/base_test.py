from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .helpers import create_user


class BaseTest(TransactionTestCase):
    def setUp(self):
        self.credentials = {"email": "test@test.com", "password": "33992433nkl"}
        self.user = create_user()

        self.client = APIClient()

        self.url = reverse("login")
        self.register_url = reverse("register")

        self.new_user = {
            "email": "test1@test.com",
            "password": "33992433nkl",
            "first_name": "test1",
            "last_name": "test",
        }

        self.token = self.client.post(self.url, self.credentials, follow=True).json()[
            "access"
        ]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
