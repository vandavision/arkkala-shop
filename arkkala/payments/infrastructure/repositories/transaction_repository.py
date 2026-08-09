from typing import Optional
from payments.models.transaction import Transaction
from payments.application.ports.repositories import TransactionRepository

class DjangoTransactionRepository(TransactionRepository):
    def create_transaction(self, user_id: int, order_id: int, amount: int, gateway: str) -> Transaction:
        return Transaction.objects.create(user_id=user_id, order_id=order_id, amount=amount, gateway=gateway)

    def get_transaction_by_uuid(self, uuid: str) -> Optional[Transaction]:
        return Transaction.objects.filter(uuid=uuid).first()

    def update_transaction(self, transaction: Transaction, status: str, authority: str = None, ref_id: str = None, description: str = None) -> None:
        transaction.status = status
        if authority: 
            transaction.authority = authority
        if ref_id: 
            transaction.ref_id = ref_id
        if description: 
            transaction.description = description
        transaction.save(update_fields=['status', 'authority', 'ref_id', 'description'])