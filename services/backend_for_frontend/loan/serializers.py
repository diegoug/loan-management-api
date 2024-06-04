from rest_framework import serializers
from .models import Customer, Loan, Payment, PaymentDetail
from django.db.models import Sum

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetail
        fields = '__all__'

class CustomerBalanceSerializer(serializers.ModelSerializer):
    total_debt = serializers.SerializerMethodField()
    available_amount = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['external_id', 'score', 'total_debt', 'available_amount']

    def get_total_debt(self, obj):
        loans = Loan.objects.filter(customer=obj, status__in=[1, 2])
        total_debt = loans.aggregate(total=Sum('outstanding'))['total']
        return total_debt if total_debt is not None else 0

    def get_available_amount(self, obj):
        total_debt = self.get_total_debt(obj)
        return obj.score - total_debt