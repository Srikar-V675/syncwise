from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import User


class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        """
        Create test user for testing JWT authentication
        """
        self.user = User.objects.create_user(username="testuser", password="test")

    def test_obtain_token(self):
        """
        Ensure we can obtain a JWT token with valid credentials
        """
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "test"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtain_token_inavlid_credentials(self):
        """
        Ensure we can't obtain a JWT token with invalid credentials
        """
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        """
        Ensure we can refresh a JWT token
        """
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "test"}
        response = self.client.post(url, data, format="json")
        refresh_token = response.data["refresh"]

        url = reverse("token_refresh")
        data = {"refresh": refresh_token}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_refresh_token_invalid_token(self):
        """
        Ensure we can't refresh a JWT token with invalid token
        """
        url = reverse("token_refresh")
        data = {"refresh": "invalid"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
