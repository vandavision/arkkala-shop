from django.db import transaction as django_transaction
from payments.application.dto.commands import VerifyPaymentDTO
from payments.application.ports.repositories import TransactionRepository, PaymentOrderRepository
from payments.application.ports.gateways import PaymentGatewayPort

class VerifyPaymentCommand:
    """Use case for verifying a callback from a payment gateway."""
    
    def __init__(self, transaction_repo: TransactionRepository, order_repo: PaymentOrderRepository, gateway_provider: callable) -> None:
        self.transaction_repo = transaction_repo
        self.order_repo = order_repo
        self.gateway_provider = gateway_provider

    def execute(self, dto: VerifyPaymentDTO) -> object:
        transaction = self.transaction_repo.get_transaction_by_uuid(dto.transaction_uuid)
        if not transaction:
            raise ValueError("تراکنش یافت نشد.")

        if transaction.status != 'pending':
            return transaction 

        gateway: PaymentGatewayPort = self.gateway_provider(dto.gateway_name)

        if dto.status_param and dto.status_param.upper() != 'OK':
            self.transaction_repo.update_transaction(transaction, status='canceled', description="انصراف کاربر")
            return transaction

        is_success, ref_id_or_error = gateway.verify_payment(authority=dto.authority, amount=int(transaction.amount))

        with django_transaction.atomic():
            if is_success:
                self.transaction_repo.update_transaction(transaction, status='successful', ref_id=ref_id_or_error)
                self.order_repo.mark_order_as_paid(transaction.order, tracking_code=ref_id_or_error)
            else:
                self.transaction_repo.update_transaction(transaction, status='failed', description=ref_id_or_error)

        return transaction