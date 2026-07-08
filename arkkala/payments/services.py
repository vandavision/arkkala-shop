"""
Service layer for orchestrating Payments and Orders.
"""
from django.urls import reverse
from django.conf import settings
from rest_framework.request import Request

from orders.models import Order
from .models import Transaction
from .gateways import GatewayFactory


class PaymentService:
    """Service to handle business logic for transactions."""

    @staticmethod
    def initiate_payment(order: Order, gateway_name: str, request: Request) -> str:
        """
        Creates a transaction and fetches the gateway redirect URL.
        """
        if order.status != 'pending':
            raise ValueError("این سفارش قابل پرداخت نیست (احتمالاً لغو شده است).")
        if order.is_paid:
            raise ValueError("این سفارش قبلاً پرداخت شده است.")

        gateway = GatewayFactory.get_gateway(gateway_name)

        transaction = Transaction.objects.create(
            user=order.user,
            order=order,
            amount=order.payable_amount,
            gateway=gateway_name,
        )

        callback_path = reverse('payment-callback')
        
        callback_url = request.build_absolute_uri(callback_path) + f"?gateway={gateway_name}&transaction_id={transaction.uuid}"
        
        buyer_name = order.user.get_full_name() if order.user else 'کاربر مهمان'
        short_order_id = str(order.uuid).split('-')[0].upper()

        payment_url, authority = gateway.request_payment(
            amount=int(order.payable_amount),
            callback_url=callback_url,
            description=f"پرداخت سفارش {short_order_id} توسط {buyer_name}"
        )

        transaction.authority = authority
        transaction.save(update_fields=['authority'])

        return payment_url

    @staticmethod
    def verify_payment(transaction_id: str, authority: str, gateway_name: str, status_param: str) -> Transaction:
        """
        Verifies the payment and updates both Transaction and Order status.
        """
        transaction = Transaction.objects.get(uuid=transaction_id)
        
        if transaction.status != 'pending':
            return transaction 

        gateway = GatewayFactory.get_gateway(gateway_name)

        if status_param and status_param.upper() != 'OK':
            transaction.status = 'canceled'
            transaction.description = "کاربر از پرداخت انصراف داد."
            transaction.save(update_fields=['status', 'description'])
            return transaction

        is_success, ref_id_or_error = gateway.verify_payment(
            authority=authority,
            amount=int(transaction.amount)
        )

        if is_success:
            transaction.status = 'successful'
            transaction.ref_id = ref_id_or_error
            transaction.save(update_fields=['status', 'ref_id'])

            order = transaction.order
            order.is_paid = True
            order.status = 'paid'
            order.tracking_code = ref_id_or_error  
            order.save(update_fields=['is_paid', 'status', 'tracking_code'])
        else:
            transaction.status = 'failed'
            transaction.description = ref_id_or_error
            transaction.save(update_fields=['status', 'description'])

        return transaction