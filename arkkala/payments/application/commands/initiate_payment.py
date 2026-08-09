from payments.application.dto.commands import InitiatePaymentDTO
from payments.application.ports.repositories import TransactionRepository, PaymentOrderRepository
from payments.application.ports.gateways import PaymentGatewayPort
from payments.domain.exceptions import InvalidPaymentOrderException

class InitiatePaymentCommand:
    """Use case for starting a new payment process."""
    
    def __init__(self, transaction_repo: TransactionRepository, order_repo: PaymentOrderRepository, gateway_provider: callable) -> None:
        self.transaction_repo = transaction_repo
        self.order_repo = order_repo
        self.gateway_provider = gateway_provider

    def execute(self, dto: InitiatePaymentDTO) -> str:
        order = self.order_repo.get_order_by_uuid(dto.order_uuid)
        if not order:
            raise InvalidPaymentOrderException("سفارش یافت نشد.")
            
        if order.user_id and dto.user_id and order.user_id != dto.user_id:
            raise InvalidPaymentOrderException("این سفارش متعلق به شما نیست.")

        if order.status != 'pending' or order.is_paid:
            raise InvalidPaymentOrderException("سفارش قابل پرداخت نیست یا قبلاً پرداخت شده است.")

        gateway: PaymentGatewayPort = self.gateway_provider(dto.gateway_name)
        
        transaction = self.transaction_repo.create_transaction(
            user_id=order.user_id,
            order_id=order.pk,
            amount=int(order.payable_amount),
            gateway=dto.gateway_name
        )

        callback_url = f"{dto.callback_url_base}?gateway={dto.gateway_name}&transaction_id={transaction.uuid}"
        short_order_id = str(order.uuid).split('-')[0].upper()
        description = f"پرداخت سفارش {short_order_id}"

        payment_url, authority = gateway.request_payment(
            amount=int(order.payable_amount),
            callback_url=callback_url,
            description=description
        )

        self.transaction_repo.update_transaction(transaction, status='pending', authority=authority)
        return payment_url