# backend_for_frontend/tests.py
import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from django.conf import settings

class RegisterAdminViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register-admin')
        self.secret_key = settings.SINGLE_USE_ADMIN_SECRET_KEY
        self.valid_payload = {
            'secret_key': self.secret_key,
            'username': 'admin',
            'password': 'adminpassword'
        }
        self.invalid_payload = {
            'secret_key': 'wrong_secret_key',
            'username': 'admin',
            'password': 'adminpassword'
        }

    def test_register_admin_success(self):
        # Verificar que no existe un superusuario antes de la prueba
        self.assertFalse(User.objects.filter(is_superuser=True).exists())
        
        response = self.client.post(self.url, data=self.valid_payload)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['message'], 'Admin user created successfully')
        self.assertTrue(User.objects.filter(is_superuser=True).exists())

    def test_register_admin_with_invalid_secret_key(self):
        response = self.client.post(self.url, data=self.invalid_payload)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_data['error'], 'Invalid secret key')

    def test_register_admin_missing_parameters(self):
        # Faltan todos los parámetros
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 400)

        # Faltan parámetros individuales
        for field in ['secret_key', 'username', 'password']:
            invalid_data = self.valid_payload.copy()
            del invalid_data[field]
            response = self.client.post(self.url, data=invalid_data)
            self.assertEqual(response.status_code, 400)

    def test_register_admin_already_exists(self):
        # Crear un superusuario inicial
        User.objects.create_superuser(username='existing_admin', password='adminpassword')

        response = self.client.post(self.url, data=self.valid_payload)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['error'], 'Admin user already exists')
