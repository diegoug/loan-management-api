# loan/tests/test_customer_view_set.py
import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_api_key.models import APIKey
from loan.models import Customer
from django.conf import settings


class CustomerViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_admin_url = reverse('register-admin')
        self.register_user_url = reverse('register-user')
        self.customer_url = reverse('customer-list')
        self.admin_payload = {
            'secret_key': settings.SINGLE_USE_CREATE_CUSTOMER_SECRET_KEY,
            'username': 'admin',
            'password': 'adminpassword'
        }
        
        response = self.client.post(self.register_admin_url, data=self.admin_payload)
        self.admin_api_key = json.loads(response.content)['api_key']
        self.client.credentials(HTTP_AUTHORIZATION='Api-Key ' + self.admin_api_key)
        
        self.user_payload = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.register_user_url, data=self.user_payload)
        self.user_api_key = json.loads(response.content)['api_key']

    def test_create_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION='Api-Key ' + self.admin_api_key)
        customer_payload = {
            'external_id': 'external_01',
            'score': 4000.0,
            'preapproved_at': '2023-02-12T22:29:27.177914Z'
        }
        response = self.client.post(self.customer_url, data=customer_payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Customer.objects.filter(external_id='external_01').exists())

    def test_create_multiple_customers(self):
        self.client.credentials(HTTP_AUTHORIZATION='Api-Key ' + self.admin_api_key)
        customers_payload = [
            {
                'external_id': 'external_01',
                'score': 4000.0,
                'preapproved_at': '2023-02-12T22:29:27.177914Z'
            },
            {
                'external_id': 'external_02',
                'score': 3000.0,
                'preapproved_at': '2023-02-13T22:29:27.177914Z'
            }
        ]
        response = self.client.post(self.customer_url, data=customers_payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Customer.objects.filter(external_id='external_01').exists())
        self.assertTrue(Customer.objects.filter(external_id='external_02').exists())

    def test_get_customer_balance(self):
        self.client.credentials(HTTP_AUTHORIZATION='Api-Key ' + self.admin_api_key)
        customer_payload = {
            'external_id': 'external_01',
            'score': 4000.0,
            'preapproved_at': '2023-02-12T22:29:27.177914Z'
        }
        self.client.post(self.customer_url, data=customer_payload, format='json')
        
        customer = Customer.objects.get(external_id='external_01')
        balance_url = reverse('customer-balance', args=[customer.id])
        
        response = self.client.get(balance_url)
        self.assertEqual(response.status_code, 200)
        balance_data = json.loads(response.content)
        self.assertEqual(balance_data['external_id'], 'external_01')
        self.assertEqual(float(balance_data['score']), 4000.0)
        self.assertEqual(float(balance_data['available_amount']), 4000.0)
        self.assertEqual(float(balance_data['total_debt']), 0)
