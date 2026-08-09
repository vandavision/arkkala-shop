from datetime import timedelta
from django.utils.timezone import now
from orders.application.dto.commands import OrderRequestCommandDTO
from orders.application.ports.repositories import OrderRepository
from orders.domain.exceptions import InvalidOrderActionException


class CreateOrderRequestCommand:
    """Use case for handling user order cancellation or return requests."""

    def __init__(self, order_repo: OrderRepository) -> None:
        self.order_repo = order_repo

    def execute(self, dto: OrderRequestCommandDTO) -> object:
        order = self.order_repo.get_user_order(dto.user_id, dto.order_uuid)
        if not order:
            raise InvalidOrderActionException("سفارش یافت نشد یا متعلق به شما نیست.")
            
        if hasattr(order, 'action_request'):
            raise InvalidOrderActionException("برای این سفارش قبلا درخواست ثبت شده است.")

        if dto.request_type == 'cancel':
            if order.status not in ['pending', 'paid', 'processing']:
                raise InvalidOrderActionException("فقط سفارشات در انتظار پرداخت، پرداخت شده یا در حال پردازش قابل لغو هستند.")
                
        elif dto.request_type == 'return':
            if order.status != 'delivered':
                raise InvalidOrderActionException("فقط سفارشات تحویل داده شده قابل مرجوعی هستند.")
                
            if (now() - order.modified_at) > timedelta(days=7):
                raise InvalidOrderActionException("مهلت ۷ روزه مرجوعی این سفارش به پایان رسیده است.")
        else:
            raise InvalidOrderActionException("نوع درخواست نامعتبر است.")

        return self.order_repo.create_order_request(order, dto.request_type, dto.reason)