from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CustomerViewSet, LoanViewSet, PaymentViewSet, 
                    PaymentDetailViewSet)

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'loans', LoanViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'payment-details', PaymentDetailViewSet)

urlpatterns = [
    path('', include(router.urls)),
]