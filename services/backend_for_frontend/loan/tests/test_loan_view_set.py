import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_api_key.models import APIKey
from loan.models import Customer, Loan
from django.conf import settings
from decimal import Decimal


class LoanViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_admin_url = reverse('register-admin')
        self.register_user_url = reverse('register-user')
        self.customer_url = reverse('customer-list')
        self.loan_url = reverse('loan-list')
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

        customer_payload = {
            'external_id': 'external_01',
            'score': 4000.0,
            'preapproved_at': '2023-02-12T22:29:27.177914Z'
        }
        self.client.post(self.customer_url, data=customer_payload, format='json')
        self.customer = Customer.objects.get(external_id='external_01')

    def test_create_loan(self):
        """
        Test creating a new loan successfully.
        """
        loan_payload = {
            'external_id': 'external_01-01',
            'customer': self.customer.id,
            'amount': 500.0,
            'contract_version': '1.0',
            'maximum_payment_date': '2024-02-12T22:29:27.177914Z'
        }
        response = self.client.post(self.loan_url, data=loan_payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Loan.objects.filter(external_id='external_01-01').exists())
        created_loan = Loan.objects.get(external_id='external_01-01')
        self.assertEqual(created_loan.status, 1)  # Check if status is Active
        self.assertEqual(created_loan.outstanding, Decimal('500.00')) 

    def test_create_loan_exceeding_credit_limit(self):
        """
        Test creating a loan that exceeds the customer's credit limit.
        Should return a 400 Bad Request.
        """
        loan_payload = {
            'external_id': 'external_01-02',
            'customer': self.customer.id,
            'amount': 5000.0,  # Exceeds the credit limit
            'contract_version': '1.0',
            'maximum_payment_date': '2024-02-12T22:29:27.177914Z'
        }
        response = self.client.post(self.loan_url, data=loan_payload, format='json')
        self.assertEqual(response.status_code, 400)  # Should return Bad Request
        self.assertFalse(Loan.objects.filter(external_id='external_01-02').exists())

    def test_get_loan_by_id(self):
        """
        Test retrieving a loan by its ID.
        """
        loan_payload = {
            'external_id': 'external_01-01',
            'customer': self.customer.id,
            'amount': 500.0,
            'contract_version': '1.0',
            'maximum_payment_date': '2024-02-12T22:29:27.177914Z'
        }
        self.client.post(self.loan_url, data=loan_payload, format='json')
        created_loan = Loan.objects.get(external_id='external_01-01')
        loan_detail_url = reverse('loan-detail', kwargs={'pk': created_loan.id})
        response = self.client.get(loan_detail_url)
        self.assertEqual(response.status_code, 200)
        loan_data = json.loads(response.content)
        self.assertEqual(loan_data['external_id'], 'external_01-01')
        self.assertEqual(Decimal(loan_data['amount']), Decimal('500.00'))

    def test_list_loans(self):
        """
        Test listing all existing loans.
        """
        loan_payload1 = {
            'external_id': 'external_01-01',
            'customer': self.customer.id,
            'amount': 500.0,
            'contract_version': '1.0',
            'maximum_payment_date': '2024-02-12T22:29:27.177914Z'
        }
        loan_payload2 = {
            'external_id': 'external_01-02',
            'customer': self.customer.id,
            'amount': 1000.0,
            'contract_version': '1.0',
            'maximum_payment_date': '2024-03-12T22:29:27.177914Z'
        }
        self.client.post(self.loan_url, data=loan_payload1, format='json')
        self.client.post(self.loan_url, data=loan_payload2, format='json')

        response = self.client.get(self.loan_url)
        self.assertEqual(response.status_code, 200)
        loans_data = json.loads(response.content)
        self.assertEqual(len(loans_data), 2)  

    def test_update_loan(self):
        """
        Test updating an existing loan.
        """
        loan_payload = {
            'external_id': 'external_01-01',
            'customer': self.customer.id,
            'amount': 500.0,
            'contract_version': '1.0',
            'maximum_payment_date': '2024-02-12T22:29:27.177914Z'
        }
        self.client.post(self.loan_url, data=loan_payload, format='json')
        created_loan = Loan.objects.get(external_id='external_01-01')
        loan_detail_url = reverse('loan-detail', kwargs={'pk': created_loan.id})

        updated_data = {
            'amount': 600.0,
            'contract_version': '1.1'
        }
        response = self.client.patch(loan_detail_url, data=updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        updated_loan = Loan.objects.get(external_id='external_01-01')
        self.assertEqual(Decimal(updated_loan.amount), Decimal('600.00'))
        self.assertEqual(updated_loan.contract_version, '1.1')

    def test_delete_loan(self):
        """
        Test deleting an existing loan.
        """
        loan_payload = {
            'external_id': 'external_01-01',
            'customer': self.customer.id,
            'amount': 500.0,
            'contract_version': '1.0',
            'maximum_payment_date': '2024-02-12T22:29:27.177914Z'
        }
        self.client.post(self.loan_url, data=loan_payload, format='json')
        created_loan = Loan.objects.get(external_id='external_01-01')
        loan_detail_url = reverse('loan-detail', kwargs={'pk': created_loan.id})

        response = self.client.delete(loan_detail_url)
        self.assertEqual(response.status_code, 204)  # No content for successful delete
        self.assertFalse(Loan.objects.filter(external_id='external_01-01').exists())