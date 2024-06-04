import json
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.conf import settings
from loan.models import Customer, Loan, Payment, PaymentDetail


class PaymentViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_admin_url = reverse('register-admin')
        self.register_user_url = reverse('register-user')
        self.customer_url = reverse('customer-list')
        self.loan_url = reverse('loan-list')
        self.payment_url = reverse('payment-list')
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

        # Create a customer for tests
        customer_payload = {
            'external_id': 'external_01',
            'score': 4000.0,
            'preapproved_at': '2023-02-12T22:29:27.177914Z'
        }
        self.client.post(self.customer_url, data=customer_payload, format='json')
        self.customer = Customer.objects.get(external_id='external_01')

        # Create loans for the customer
        loan_payload1 = {
            'external_id': 'external_01-01',
            'customer': self.customer.id,
            'amount': 1000.0,
            'contract_version': '1.0',
            'maximum_payment_date': '2024-02-12T22:29:27.177914Z'
        }
        loan_payload2 = {
            'external_id': 'external_01-02',
            'customer': self.customer.id,
            'amount': 500.0,
            'contract_version': '1.0',
            'maximum_payment_date': '2024-03-12T22:29:27.177914Z'
        }
        self.client.post(self.loan_url, data=loan_payload1, format='json')
        self.client.post(self.loan_url, data=loan_payload2, format='json')
        self.loan1 = Loan.objects.get(external_id='external_01-01')
        self.loan2 = Loan.objects.get(external_id='external_01-02')

    def test_create_payment_success(self):
        payment_payload = {
            'external_id': 'payment_01',
            'customer': self.customer.id,
            'total_amount': 500.0,
            'paid_at': '2023-06-12T12:00:00Z'
        }
        response = self.client.post(self.payment_url, data=payment_payload, format='json')
        self.assertEqual(response.status_code, 201)

        # Assertions
        self.assertTrue(Payment.objects.filter(external_id='payment_01').exists())
        payment = Payment.objects.get(external_id='payment_01')
        self.assertTrue(PaymentDetail.objects.filter(payment=payment).exists())
        self.loan1.refresh_from_db()
        self.assertEqual(self.loan1.outstanding, Decimal('500.00'))

    def test_create_payment_exceeding_debt(self):
        payment_payload = {
            'external_id': 'payment_02',
            'customer': self.customer.id,
            'total_amount': 2000.0,
            'paid_at': '2023-06-12T12:00:00Z'
        }
        response = self.client.post(self.payment_url, data=payment_payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
        self.assertFalse(Payment.objects.filter(external_id='payment_02').exists())
        self.loan1.refresh_from_db()
        self.assertEqual(self.loan1.outstanding, Decimal('1000.00'))

    def test_create_payment_multiple_loans(self):
        payment_payload = {
            'external_id': 'payment_03',
            'customer': self.customer.id,
            'total_amount': 1500.0,
            'paid_at': '2023-06-12T12:00:00Z'
        }
        response = self.client.post(self.payment_url, data=payment_payload, format='json')
        self.assertEqual(response.status_code, 201)

        self.loan1.refresh_from_db()
        self.loan2.refresh_from_db()
        self.assertEqual(self.loan1.outstanding, Decimal('0.00')) 
        self.assertEqual(self.loan2.outstanding, Decimal('0.00'))  
        self.assertEqual(self.loan1.status, 4)  
        self.assertEqual(self.loan2.status, 4) 

    def test_get_payment_by_id(self):
        payment_payload = {
            'external_id': 'payment_01',
            'customer': self.customer.id,
            'total_amount': 500.0,
            'paid_at': '2023-06-12T12:00:00Z'
        }
        self.client.post(self.payment_url, data=payment_payload, format='json')
        payment = Payment.objects.get(external_id='payment_01')
        payment_detail_url = reverse('payment-detail', kwargs={'pk': payment.id})

        response = self.client.get(payment_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['external_id'], 'payment_01')

    def test_list_payments(self):
        payment_payload1 = {
            'external_id': 'payment_01',
            'customer': self.customer.id,
            'total_amount': 500.0,
            'paid_at': '2023-06-12T12:00:00Z'
        }
        payment_payload2 = {
            'external_id': 'payment_02',
            'customer': self.customer.id,
            'total_amount': 300.0,
            'paid_at': '2023-06-13T12:00:00Z'
        }
        self.client.post(self.payment_url, data=payment_payload1, format='json')
        self.client.post(self.payment_url, data=payment_payload2, format='json')

        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), 2)

    def test_update_payment(self):
        payment_payload = {
            'external_id': 'payment_01',
            'customer': self.customer.id,
            'total_amount': 500.0,
            'paid_at': '2023-06-12T12:00:00Z'
        }
        self.client.post(self.payment_url, data=payment_payload, format='json')
        payment = Payment.objects.get(external_id='payment_01')
        payment_detail_url = reverse('payment-detail', kwargs={'pk': payment.id})

        updated_data = {
            'total_amount': 600.0,
        }
        response = self.client.patch(payment_detail_url, data=updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.total_amount, Decimal('600.00'))

    def test_delete_payment(self):
        """Test deleting a payment."""
        payment_payload = {
            'external_id': 'payment_01',
            'customer': self.customer.id,
            'total_amount': 500.0,
            'paid_at': '2023-06-12T12:00:00Z'
        }
        response = self.client.post(self.payment_url, data=payment_payload, format='json')
        payment = Payment.objects.get(external_id='payment_01')
        payment_detail_url = reverse('payment-detail', kwargs={'pk': payment.id})

        response = self.client.delete(payment_detail_url)
        self.assertEqual(response.status_code, 204) 
        self.assertFalse(Payment.objects.filter(external_id='payment_01').exists())

    def test_create_payment_sets_pending_status(self):
        payment_payload = {
            'external_id': 'payment_01',
            'customer': self.customer.id,
            'total_amount': 500.0,
            'paid_at': '2023-06-12T12:00:00Z'
        }
        response = self.client.post(self.payment_url, data=payment_payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.content)['status'], 1)  # 1: "pending"

    def test_confirm_payment(self):
        payment_payload = {
            'external_id': 'payment_01',
            'customer': self.customer.id,
            'total_amount': 500.0,
            'paid_at': '2023-06-12T12:00:00Z'
        }
        self.client.post(self.payment_url, data=payment_payload, format='json')
        payment = Payment.objects.get(external_id='payment_01')

        confirm_url = reverse('payment-confirm', kwargs={'pk': payment.id})
        response = self.client.patch(confirm_url, data={'status': 2}, format='json')  # 2: "completed"
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 2)