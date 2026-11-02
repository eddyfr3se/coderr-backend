"""Model checks for user profiles before the API is implemented."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import UserProfile


class UserProfileTests(APITestCase):
    """Check profile validation, defaults and user relationships."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='profile_test',
        )

    def test_customer_and_business_are_valid_types(self):
        for user_type in ['customer', 'business']:
            with self.subTest(user_type=user_type):
                profile = UserProfile(user=self.user, type=user_type)
                profile.full_clean()

    def test_invalid_type_is_rejected_by_model_validation(self):
        profile = UserProfile(user=self.user, type='unknown')

        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_optional_fields_can_remain_empty(self):
        profile = UserProfile.objects.create(user=self.user, type='customer')
        profile.refresh_from_db()

        for field in ['location', 'tel', 'description', 'working_hours']:
            self.assertEqual(getattr(profile, field), '')
        self.assertFalse(profile.file)
        self.assertIsNotNone(profile.created_at)
        self.assertEqual(str(profile), self.user.username)

    def test_duplicate_profile_is_rejected_by_model_validation(self):
        UserProfile.objects.create(user=self.user, type='customer')
        duplicate = UserProfile(user=self.user, type='business')

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_deleting_user_also_deletes_profile(self):
        profile = UserProfile.objects.create(user=self.user, type='customer')
        profile_id = profile.pk

        self.user.delete()

        self.assertFalse(UserProfile.objects.filter(pk=profile_id).exists())

    def test_deleting_profile_preserves_user(self):
        profile = UserProfile.objects.create(user=self.user, type='customer')
        user_id = self.user.pk

        profile.delete()

        self.assertTrue(get_user_model().objects.filter(pk=user_id).exists())


class AuthenticationTests(APITestCase):
    """Exercise registration and login through their actual API routes."""

    def setUp(self):
        self.password = 'Local-test-password-53!'
        self.data = {
            'username': 'auth_test_customer',
            'email': 'auth_test@coderr.example',
            'password': self.password,
            'repeated_password': self.password,
            'type': 'customer',
        }

    def register(self, **changes):
        data = {**self.data, **changes}
        return self.client.post(reverse('registration'), data, format='json')

    def login(self, **changes):
        data = {'username': self.data['username'], 'password': self.password}
        data.update(changes)
        return self.client.post(reverse('login'), data, format='json')

    def assert_auth_response(self, response, expected_status):
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(
            set(response.data), {'token', 'username', 'email', 'user_id'},
        )
        token = Token.objects.get(key=response.data['token'])
        self.assertEqual(token.user_id, response.data['user_id'])

    def test_customer_registration_creates_user_profile_and_token(self):
        response = self.register()

        self.assert_auth_response(response, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(pk=response.data['user_id'])
        self.assertTrue(user.check_password(self.password))
        self.assertNotEqual(user.password, self.password)
        self.assertEqual(user.profile.type, 'customer')
        self.assertEqual(user.username, self.data['username'])
        self.assertEqual(user.email, self.data['email'])

    def test_business_registration_creates_business_profile(self):
        response = self.register(type='business')

        self.assert_auth_response(response, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(pk=response.data['user_id'])
        self.assertEqual(user.profile.type, 'business')

    def test_mismatched_passwords_do_not_create_account(self):
        response = self.register(repeated_password='different-password')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('repeated_password', response.data)
        self.assertFalse(get_user_model().objects.exists())

    def test_duplicate_username_is_rejected(self):
        self.register()

        response = self.register(email='another@coderr.example')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_duplicate_email_is_rejected_case_insensitively(self):
        self.register()

        response = self.register(
            username='another_user', email=self.data['email'].upper(),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_invalid_role_and_email_are_rejected(self):
        for changes in ({'type': 'admin'}, {'email': 'invalid'}):
            with self.subTest(changes=changes):
                response = self.register(**changes)
                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST,
                )
        self.assertFalse(get_user_model().objects.exists())

    def test_every_registration_field_is_required(self):
        for field in self.data:
            with self.subTest(field=field):
                data = self.data.copy()
                data.pop(field)
                response = self.client.post(
                    reverse('registration'), data, format='json',
                )
                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST,
                )
        self.assertFalse(get_user_model().objects.exists())

    def test_login_returns_the_existing_token(self):
        registration = self.register()

        response = self.login()

        self.assert_auth_response(response, status.HTTP_200_OK)
        self.assertEqual(response.data, registration.data)
        self.assertEqual(Token.objects.count(), 1)

    def test_wrong_password_and_unknown_user_are_rejected(self):
        self.register()
        for changes in ({'password': 'wrong'}, {'username': 'missing_user'}):
            with self.subTest(changes=changes):
                response = self.login(**changes)
                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST,
                )

    def test_inactive_user_cannot_login(self):
        self.register()
        get_user_model().objects.update(is_active=False)

        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_login_fields_are_rejected(self):
        for data in ({}, {'username': 'someone'}, {'password': self.password}):
            with self.subTest(data=data):
                response = self.client.post(reverse('login'), data)
                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST,
                )

    def test_auth_endpoints_do_not_accept_get(self):
        for name in ['registration', 'login']:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(
                    response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED,
                )
