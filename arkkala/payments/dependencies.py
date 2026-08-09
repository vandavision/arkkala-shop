from payments.infrastructure.repositories.transaction_repository import DjangoTransactionRepository
from payments.infrastructure.repositories.order_repository import DjangoPaymentOrderRepository
from payments.infrastructure.gateways.zarinpal import get_gateway_provider
from payments.application.commands.initiate_payment import InitiatePaymentCommand
from payments.application.commands.verify_payment import VerifyPaymentCommand


def get_initiate_payment_command() -> InitiatePaymentCommand:
    return InitiatePaymentCommand(
        transaction_repo=DjangoTransactionRepository(),
        order_repo=DjangoPaymentOrderRepository(),
        gateway_provider=get_gateway_provider
    )

def get_verify_payment_command() -> VerifyPaymentCommand:
    return VerifyPaymentCommand(
        transaction_repo=DjangoTransactionRepository(),
        order_repo=DjangoPaymentOrderRepository(),
        gateway_provider=get_gateway_provider
    )