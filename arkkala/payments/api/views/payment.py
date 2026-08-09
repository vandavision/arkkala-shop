from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request

from payments.models.transaction import Transaction
from payments.api.serializers.inputs.payment import PaymentRequestInputSerializer
from payments.api.serializers.outputs.transaction import TransactionOutputSerializer
from payments.application.dto.commands import InitiatePaymentDTO, VerifyPaymentDTO
from payments.domain.exceptions import PaymentDomainException
import payments.dependencies as deps


class PaymentViewSet(viewsets.GenericViewSet):
    """ViewSet for Payments handling requests and callbacks."""
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Transaction.objects.filter(user=self.request.user)
        return Transaction.objects.none()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def request_payment(self, request: Request) -> Response:
        serializer = PaymentRequestInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        callback_base = request.build_absolute_uri(reverse('payment-callback'))
        
        dto = InitiatePaymentDTO(
            user_id=request.user.id if request.user.is_authenticated else None,
            order_uuid=str(serializer.validated_data['order_id']),
            gateway_name=serializer.validated_data['gateway'],
            callback_url_base=callback_base
        )

        try:
            payment_url = deps.get_initiate_payment_command().execute(dto)
            return Response({"payment_url": payment_url}, status=status.HTTP_200_OK)
        except (ValueError, PaymentDomainException) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get', 'post'], url_path='callback', url_name='callback')
    def callback(self, request: Request):
        gateway_name = request.GET.get('gateway')
        transaction_id = request.GET.get('transaction_id')
        authority = request.GET.get('Authority')  
        status_param = request.GET.get('Status')  

        if not transaction_id or not authority:
            return Response({"error": "پارامترهای بازگشتی نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)

        dto = VerifyPaymentDTO(
            transaction_uuid=transaction_id, authority=authority,
            gateway_name=gateway_name, status_param=status_param
        )

        try:
            transaction = deps.get_verify_payment_command().execute(dto)
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            redirect_url = f"{frontend_url}/payment/result?status={transaction.status}&ref_id={transaction.ref_id or ''}&order_id={transaction.order.uuid}"
            return redirect(redirect_url)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def history(self, request: Request) -> Response:
        transactions = self.get_queryset()
        serializer = TransactionOutputSerializer(transactions, many=True)
        return Response(serializer.data)