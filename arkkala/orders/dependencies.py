from orders.infrastructure.repositories.cart_repository import DjangoCartRepository
from orders.infrastructure.repositories.order_repository import DjangoOrderRepository
from orders.infrastructure.repositories.coupon_repository import DjangoCouponRepository
from orders.infrastructure.repositories.shipping_repository import DjangoShippingRepository
from orders.infrastructure.repositories.inventory_repository import DjangoInventoryRepository
from orders.infrastructure.repositories.customer_repository import DjangoCustomerRepository
from orders.infrastructure.providers.postex import PostexShippingProvider
from orders.infrastructure.messaging.event_bus import DjangoEventBus

from orders.application.commands.checkout import CheckoutCommand
from orders.application.commands.create_order_request import CreateOrderRequestCommand


def get_checkout_command() -> CheckoutCommand:
    """DI Container builder for CheckoutCommand."""
    return CheckoutCommand(
        cart_repo=DjangoCartRepository(),
        order_repo=DjangoOrderRepository(),
        coupon_repo=DjangoCouponRepository(),
        shipping_repo=DjangoShippingRepository(),
        inventory_repo=DjangoInventoryRepository(),
        customer_repo=DjangoCustomerRepository(),
        shipping_provider=PostexShippingProvider(),
        event_bus=DjangoEventBus()
    )


def get_order_request_command() -> CreateOrderRequestCommand:
    """DI Container builder for CreateOrderRequestCommand."""
    return CreateOrderRequestCommand(
        order_repo=DjangoOrderRepository()
    )