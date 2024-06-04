# backend_for_frontend/tests/test_register_user_view_test.py
import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from django.conf import settings


class RegisterUserViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_admin_url = reverse('register-admin')
        self.register_user_url = reverse('register-user')
        self.admin_payload = {
            'secret_key': settings.SINGLE_USE_CREATE_CUSTOMER_SECRET_KEY,
            'username': 'admin',
            'password': 'adminpassword'
        }

        response = self.client.post(self.register_admin_url, data=self.admin_payload)
        self.admin_api_key = json.loads(response.content)['api_key']
        self.client.credentials(HTTP_AUTHORIZATION='Api-Key ' + self.admin_api_key)

    def test_admin_can_create_user(self):
        valid_payload = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.register_user_url, data=valid_payload)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertIn('api_key', response_data)

    def test_admin_can_create_admin(self):
        valid_payload = {
            'username': 'newadmin',
            'password': 'newadminpassword',
            'is_admin': True
        }
        response = self.client.post(self.register_user_url, data=valid_payload)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username='newadmin', is_superuser=True).exists())
        self.assertIn('api_key', response_data)

    def test_user_cannot_create_admin(self):
        user_payload = {
            'username': 'user',
            'password': 'userpassword'
        }
        response = self.client.post(self.register_user_url, data=user_payload)
        user_api_key = json.loads(response.content)['api_key']
        self.client.credentials(HTTP_AUTHORIZATION='Api-Key ' + user_api_key)
        
        invalid_payload = {
            'username': 'unauthorizedadmin',
            'password': 'adminpassword',
            'is_admin': True
        }
        response = self.client.post(self.register_user_url, data=invalid_payload)
        self.assertEqual(response.status_code, 403)
