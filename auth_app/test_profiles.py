"""Checks for profile serialization before endpoint integration."""

from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.api.serializers import (
    BusinessProfileSerializer,
    CustomerProfileSerializer,
    ProfileUpdateSerializer,
)
from auth_app.models import UserProfile


class ProfileUpdateSerializerTests(APITestCase):
    """Check partial changes across the user and profile models."""

    def setUp(self):
        """Prepare isolated fixtures for the tests in this class."""
        self.user = get_user_model().objects.create_user(
            username='profile_update_test', email='profile@coderr.example',
            first_name='Alex', last_name='Muster',
        )
        self.profile = UserProfile.objects.create(
            user=self.user, type='customer', location='Berlin',
        )

    def test_partial_update_preserves_omitted_fields(self):
        """Verify that partial update preserves omitted fields."""
        serializer = ProfileUpdateSerializer(
            self.profile, data={'first_name': 'Mara', 'tel': '+49 030 123'},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Mara')
        self.assertEqual(self.profile.tel, '+49 030 123')
        self.assertEqual(self.user.last_name, 'Muster')
        self.assertEqual(self.profile.location, 'Berlin')
        self.assertEqual(self.profile.type, 'customer')

    def test_email_used_by_another_user_is_rejected(self):
        """Verify that email used by another user is rejected."""
        get_user_model().objects.create_user(
            username='other_profile_test', email='other@coderr.example',
        )
        serializer = ProfileUpdateSerializer(
            self.profile, data={'email': 'OTHER@coderr.example'}, partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_own_email_remains_valid(self):
        """Verify that own email remains valid."""
        serializer = ProfileUpdateSerializer(
            self.profile, data={'email': self.user.email}, partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)


class ProfileListSerializerTests(APITestCase):
    """Test profile list serializer."""
    def setUp(self):
        """Prepare isolated fixtures for the tests in this class."""
        self.user = get_user_model().objects.create_user(username='list_test')
        self.profile = UserProfile.objects.create(
            user=self.user, type='customer',
        )

    def test_business_profile_fields(self):
        """Verify that business profile fields."""
        self.profile.type = 'business'
        data = BusinessProfileSerializer(self.profile).data
        self.assertEqual(set(data), {
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
        })
        for field in ('first_name', 'last_name', 'location', 'tel',
                      'description', 'working_hours'):
            self.assertEqual(data[field], '')

    def test_customer_profile_fields(self):
        """Verify that customer profile fields."""
        data = CustomerProfileSerializer(self.profile).data
        self.assertEqual(set(data), {
            'user', 'username', 'first_name', 'last_name', 'file',
            'uploaded_at', 'type',
        })
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['type'], 'customer')
        self.assertTrue(data['uploaded_at'])


class ProfileListEndpointTests(APITestCase):
    """Test profile list endpoint."""
    def setUp(self):
        """Prepare isolated fixtures for the tests in this class."""
        self.users = {}
        self.urls = {}
        for role in ('business', 'customer'):
            user = get_user_model().objects.create_user(username=role)
            UserProfile.objects.create(user=user, type=role)
            self.users[role] = user
            self.urls[role] = reverse(f'{role}-profile-list')

    def authenticate(self, role):
        """Attach a test user token to subsequent API requests."""
        token, _ = Token.objects.get_or_create(user=self.users[role])
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_anonymous_access_is_rejected(self):
        """Verify that anonymous access is rejected."""
        for url in self.urls.values():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code, status.HTTP_401_UNAUTHORIZED,
                )

    def test_both_roles_can_read_both_filtered_lists(self):
        """Verify that both roles can read both filtered lists."""
        for reader in self.users:
            self.authenticate(reader)
            for role, url in self.urls.items():
                with self.subTest(reader=reader, role=role):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    self.assertIsInstance(response.data, list)
                    self.assertEqual(len(response.data), 1)
                    self.assertEqual(response.data[0]['type'], role)
                    self.assertEqual(
                        response.data[0]['user'], self.users[role].pk,
                    )

    def test_empty_lists_are_returned_as_arrays(self):
        """Verify that empty lists are returned as arrays."""
        self.authenticate('customer')
        UserProfile.objects.all().delete()
        for url in self.urls.values():
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data, [])

    def test_write_methods_are_rejected(self):
        """Verify that write methods are rejected."""
        self.authenticate('business')
        for url in self.urls.values():
            for method in ('post', 'put', 'patch', 'delete'):
                with self.subTest(url=url, method=method):
                    response = getattr(self.client, method)(url)
                    self.assertEqual(
                        response.status_code,
                        status.HTTP_405_METHOD_NOT_ALLOWED,
                    )

    def test_lists_load_users_without_extra_queries_per_profile(self):
        """Verify that lists load users without extra queries per profile."""
        self.authenticate('customer')
        for role in self.users:
            user = get_user_model().objects.create_user(username=f'{role}_2')
            UserProfile.objects.create(user=user, type=role)
        for url in self.urls.values():
            with self.subTest(url=url):
                with self.assertNumQueries(2):
                    response = self.client.get(url)
                    self.assertEqual(len(response.data), 2)


class ProfileEndpointTests(APITestCase):
    """Test profile endpoint."""
    def setUp(self):
        """Prepare isolated fixtures for the tests in this class."""
        self.other = get_user_model().objects.create_user(username='other')
        self.owner = get_user_model().objects.create_user(username='owner')
        self.profile = UserProfile.objects.create(
            user=self.owner, type='customer', location='Berlin',
        )
        self.url = reverse('profile-detail', kwargs={'pk': self.owner.pk})

    def prepare_upload(self):
        """Prepare a sample image and a temporary media directory."""
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        settings = override_settings(MEDIA_ROOT=directory.name)
        settings.enable()
        self.addCleanup(settings.disable)
        content = (
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,'
            b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        )
        return SimpleUploadedFile('testbild.gif', content, 'image/gif')

    def authenticate(self, user):
        """Attach a test user token to subsequent API requests."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_anonymous_requests_are_rejected(self):
        """Verify that anonymous requests are rejected."""
        for method in ('get', 'patch'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.url)
                self.assertEqual(
                    response.status_code, status.HTTP_401_UNAUTHORIZED,
                )

    def test_other_user_can_read_profile_by_user_id(self):
        """Verify that other user can read profile by user id."""
        self.authenticate(self.other)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.owner.pk)
        self.assertEqual(response.data['username'], 'owner')
        self.assertNotIn('password', response.data)

    def test_owner_can_patch_and_receives_full_profile(self):
        """Verify that owner can patch and receives full profile."""
        self.authenticate(self.owner)
        response = self.client.patch(
            self.url, {'first_name': 'Mara'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Mara')
        self.assertEqual(response.data['location'], 'Berlin')
        self.assertEqual(response.data['type'], 'customer')
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.first_name, 'Mara')

    def test_other_user_cannot_patch_profile(self):
        """Verify that other user cannot patch profile."""
        self.authenticate(self.other)
        response = self.client.patch(self.url, {'location': 'Hamburg'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.location, 'Berlin')

    def test_missing_profile_returns_not_found(self):
        """Verify that missing profile returns not found."""
        self.authenticate(self.owner)
        url = reverse('profile-detail', kwargs={'pk': self.other.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_undocumented_methods_are_rejected(self):
        """Verify that undocumented methods are rejected."""
        self.authenticate(self.owner)
        for method in ('post', 'put', 'delete'):
            with self.subTest(method=method):
                response = getattr(self.client, method)(self.url)
                self.assertEqual(
                    response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED,
                )

    def test_owner_can_upload_file(self):
        """Verify that owner can upload file."""
        upload = self.prepare_upload()
        expected = upload.read()
        upload.seek(0)
        self.authenticate(self.owner)
        response = self.client.patch(self.url, {'file': upload})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.file.name.startswith('profiles/'))
        self.assertIn('/media/profiles/', response.data['file'])
        with self.profile.file.open('rb') as saved:
            self.assertEqual(saved.read(), expected)
        self.assertEqual(self.profile.location, 'Berlin')

    def test_other_user_cannot_upload_file(self):
        """Verify that other user cannot upload file."""
        upload = self.prepare_upload()
        self.authenticate(self.other)
        response = self.client.patch(self.url, {'file': upload})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.file)

    def test_empty_file_is_rejected(self):
        """Verify that empty file is rejected."""
        self.prepare_upload()
        self.authenticate(self.owner)
        upload = SimpleUploadedFile('empty.gif', b'', 'image/gif')
        response = self.client.patch(self.url, {'file': upload})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.file)
