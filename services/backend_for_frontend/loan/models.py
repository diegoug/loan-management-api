# loans/models.py
from django.db import models

# Definición de choices reutilizables
CUSTOMER_STATUS_CHOICES = [
    (1, 'Active'),
    (2, 'Inactive'),
]

LOAN_STATUS_CHOICES = [
    (1, 'Pending'),
    (2, 'Active'),
    (3, 'Rejected'),
    (4, 'Paid'),
]

PAYMENT_STATUS_CHOICES = [
    (1, 'Completed'),
    (2, 'Rejected'),
]

class Customer(models.Model):
    external_id = models.CharField(max_length=60, unique=True)
    status = models.SmallIntegerField(choices=CUSTOMER_STATUS_CHOICES)
    score = models.DecimalField(max_digits=12, decimal_places=2)
    preapproved_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.external_id

class Loan(models.Model):
    external_id = models.CharField(max_length=60, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.SmallIntegerField(choices=LOAN_STATUS_CHOICES, default=1)
    contract_version = models.CharField(max_length=30, null=True, blank=True)
    maximum_payment_date = models.DateTimeField()
    taken_at = models.DateTimeField(null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    outstanding = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.external_id

class Payment(models.Model):
    external_id = models.CharField(max_length=60, unique=True)
    total_amount = models.DecimalField(max_digits=20, decimal_places=10)
    status = models.SmallIntegerField(choices=PAYMENT_STATUS_CHOICES)
    paid_at = models.DateTimeField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.external_id

class PaymentDetail(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=10)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payment.external_id} -> {self.loan.external_id}"
