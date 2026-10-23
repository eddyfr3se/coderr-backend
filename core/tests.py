"""Basic checks for admin routing and access protection."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AdminAccessTests(APITestCase):
    """Check the admin pages before business endpoints are implemented."""

    def setUp(self):
        self.login_url = reverse('admin:login')
        self.admin_url = reverse('admin:index')
        self.staff_user = get_user_model().objects.create_user(
            username='staff_test', is_staff=True,
        )

    def test_login_page_is_accessible_without_authentication(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_visitor_is_redirected_to_login(self):
        response = self.client.get(self.admin_url)

        self.assertRedirects(
            response,
            f'{self.login_url}?next={self.admin_url}',
            fetch_redirect_response=False,
        )

    def test_staff_user_can_open_admin(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(self.admin_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
