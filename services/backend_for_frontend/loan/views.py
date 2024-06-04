from decimal import Decimal

from django.db.models import Sum

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

from .models import Customer, Loan, Payment, PaymentDetail
from .serializers import (
    CustomerSerializer, LoanSerializer, PaymentSerializer, 
    PaymentDetailSerializer, CustomerBalanceSerializer
)
from backend_for_frontend.permissions import HasCustomAPIKey


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, HasCustomAPIKey]

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if is_many:
            for customer_data in request.data:
                customer_data['status'] = 1  # Set status to Active by default
        else:
            request.data['status'] = 1  # Set status to Active by default

        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        customer = self.get_object()
        serializer = CustomerBalanceSerializer(customer)
        return Response(serializer.data)

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated, HasCustomAPIKey]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer = serializer.validated_data['customer']

        total_debt = Loan.objects.filter(customer=customer, status__in=[1, 2]).aggregate(total=Sum('outstanding'))['total'] or 0

        if serializer.validated_data['amount'] + total_debt > customer.score:
            return Response({'error': 'Loan amount exceeds customer credit limit'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.validated_data['status'] = 1 
        serializer.validated_data['outstanding'] = serializer.validated_data['amount'] 

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, HasCustomAPIKey]

    def create(self, request, *args, **kwargs):
        
        request.data['status'] = 1

        customer_id = request.data.get('customer')
        customer = Customer.objects.get(id=customer_id)
        total_debt = Loan.objects.filter(customer=customer, status__in=[1, 2]).aggregate(
            total=Sum('outstanding'))['total'] or 0

        total_amount = Decimal(request.data.get('total_amount'))

        if total_amount > total_debt:
            return Response({'error': 'Payment amount exceeds total debt'},
                            status=status.HTTP_400_BAD_REQUEST)

        payment = super().create(request, *args, **kwargs)
        payment_instance = Payment.objects.get(id=payment.data['id'])

        loans = Loan.objects.filter(customer=customer, status__in=[1, 2]).order_by(
            'maximum_payment_date')

        for loan in loans:
            if total_amount <= 0:
                break

            outstanding = loan.outstanding

            if total_amount >= outstanding:
                loan.outstanding = 0
                loan.status = 4  # Paid
                loan_instance = Loan.objects.get(id=loan.id)
                PaymentDetail.objects.create(payment=payment_instance, loan=loan_instance, amount=outstanding)
                total_amount -= outstanding
            else:
                loan.outstanding -= total_amount
                loan_instance = Loan.objects.get(id=loan.id)
                PaymentDetail.objects.create(payment=payment_instance, loan=loan_instance, amount=total_amount)
                total_amount = 0

            loan.save()

        serializer = self.get_serializer(payment_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['patch'])
    def confirm(self, request, pk=None):
        """Endpoint para confirmar un pago."""
        payment = self.get_object()
        if payment.status != 1:  # Solo se pueden confirmar pagos pendientes
            return Response({'error': 'Payment is not in pending status'}, status=status.HTTP_400_BAD_REQUEST)

        payment.status = 2
        payment.save()
        serializer = self.get_serializer(payment)
        return Response(serializer.data)


class PaymentDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentDetail.objects.all()
    serializer_class = PaymentDetailSerializer
    permission_classes = [IsAuthenticated, HasCustomAPIKey]
