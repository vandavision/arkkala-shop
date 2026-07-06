"""
API Views for handling payment requests and callbacks.
"""
from django.shortcuts import redirect
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request

from orders.models import Order
from .models import Transaction
from .serializers import PaymentRequestSerializer, TransactionSerializer
from .services import PaymentService


class PaymentViewSet(viewsets.GenericViewSet):
    """
    ViewSet for Payments.
    Provides /request/ to get payment URL and /callback/ for gateway return.
    """
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Transaction.objects.filter(user=self.request.user)
        return Transaction.objects.none()

    @action(detail=False, methods=['post'])
    def request_payment(self, request: Request) -> Response:
        """
        API to initiate a payment. Returns the Gateway redirect URL.
        """
        serializer = PaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data['order_id']
        gateway = serializer.validated_data['gateway']

        try:
            if request.user.is_authenticated:
                order = Order.objects.get(id=order_id, user=request.user)
            else:
                order = Order.objects.get(id=order_id, user__isnull=True)

            payment_url = PaymentService.initiate_payment(order, gateway, request)
            return Response({"payment_url": payment_url}, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            return Response({"error": "سفارش یافت نشد یا متعلق به شما نیست."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"خطای سیستم: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get', 'post'], permission_classes=[AllowAny], url_path='callback', url_name='callback')
    def callback(self, request: Request):
        """
        Public Callback URL. Gateways will redirect users here after payment.
        """
        gateway_name = request.GET.get('gateway')
        transaction_id = request.GET.get('transaction_id')
        authority = request.GET.get('Authority')  # Zarinpal
        status_param = request.GET.get('Status')  # Zarinpal

        if not transaction_id or not authority:
            return Response({"error": "پارامترهای بازگشتی نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            transaction = PaymentService.verify_payment(
                transaction_id=transaction_id,
                authority=authority,
                gateway_name=gateway_name,
                status_param=status_param
            )
            
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            redirect_url = f"{frontend_url}/payment/result?status={transaction.status}&ref_id={transaction.ref_id or ''}"
            return redirect(redirect_url)
            
        except Transaction.DoesNotExist:
            return Response({"error": "تراکنش یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def history(self, request: Request) -> Response:
        """Get the current user's transaction history."""
        transactions = self.get_queryset()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)