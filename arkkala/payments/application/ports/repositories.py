from abc import ABC, abstractmethod
from typing import Optional
from payments.models.transaction import Transaction
from orders.models.order import Order

class TransactionRepository(ABC):
    """Port for managing transaction persistence."""
    @abstractmethod
    def create_transaction(self, user_id: int, order_id: int, amount: int, gateway: str) -> Transaction:
        pass

    @abstractmethod
    def get_transaction_by_uuid(self, uuid: str) -> Optional[Transaction]:
        pass

    @abstractmethod
    def update_transaction(self, transaction: Transaction, status: str, authority: str = None, ref_id: str = None, description: str = None) -> None:
        pass

class PaymentOrderRepository(ABC):
    """Port for managing associated order status from payment context."""
    @abstractmethod
    def get_order_by_uuid(self, uuid: str) -> Optional[Order]:
        pass

    @abstractmethod
    def mark_order_as_paid(self, order: Order, tracking_code: str) -> None:
        pass