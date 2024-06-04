import json
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.conf import settings
from loan.models import Customer, Loan, Payment, PaymentDetail


class PaymentDetailViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_admin_url = reverse('register-admin')
        self.register_user_url = reverse('register-user')
        self.customer_url = reverse('customer-list')
        self.loan_url = reverse('loan-list')
        self.payment_url = reverse('payment-list')
        self.payment_detail_url = reverse('payment-detail-list')
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

        # Create a payment
        payment_payload = {
            'external_id': 'payment_01',
            'customer': self.customer.id,
            'total_amount': 1500.0,
            'paid_at': '2023-06-12T12:00:00Z'
        }
        self.client.post(self.payment_url, data=payment_payload, format='json')
        self.payment = Payment.objects.get(external_id='payment_01')

    def test_get_payment_detail_by_id(self):
        payment_detail = PaymentDetail.objects.get(payment=self.payment, loan=self.loan1)
        url = reverse('payment-detail-detail', kwargs={'pk': payment_detail.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['payment'], self.payment.id)
        self.assertEqual(data['loan'], self.loan1.id)
        self.assertEqual(Decimal(data['amount']), Decimal('1000.00'))

    def test_list_payment_details(self):
        response = self.client.get(self.payment_detail_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
    
    def test_create_payment_detail(self):
        payload = {
            'payment': self.payment.id,
            'loan': self.loan1.id,
            'amount': 300.0
        }
        response = self.client.post(self.payment_detail_url, data=payload, format='json')
        self.assertEqual(response.status_code, 405)  # 405 Method Not Allowed

    def test_update_payment_detail(self):
        payment_detail = PaymentDetail.objects.get(payment=self.payment, loan=self.loan1)
        url = reverse('payment-detail-detail', kwargs={'pk': payment_detail.id})
        updated_data = {'amount': 400.0}
        response = self.client.patch(url, data=updated_data, format='json')
        self.assertEqual(response.status_code, 405)  # 405 Method Not Allowed

    def test_delete_payment_detail(self):
        payment_detail = PaymentDetail.objects.get(payment=self.payment, loan=self.loan1)
        url = reverse('payment-detail-detail', kwargs={'pk': payment_detail.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 405)  # 405 Method Not Allowed
