"""
Service for ZarinPal Integration.
"""
import requests
from django.conf import settings
from typing import Tuple, Optional

from orders.models import Order, OrderStatus
from .models import Transaction, TransactionStatus

ZARINPAL_MERCHANT = getattr(settings, 'ZARINPAL_MERCHANT', 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX')
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"


class ZarinPalService:
    """ZarinPal Gateway Operations."""

    @staticmethod
    def create_transaction(order: Order, callback_url: str) -> Tuple[Optional[str], str]:
        """Request payment from ZarinPal and create Transaction record."""
        # Convert Toman to Rial for ZarinPal
        amount_rial = int(order.payable_price * 10)
        
        # Determine Contact Info (User vs Guest)
        mobile = getattr(order.user, 'mobile', order.guest_mobile) if order.user else order.guest_mobile
        email = getattr(order.user, 'email', '') if order.user else ''
        
        payload = {
            "merchant_id": ZARINPAL_MERCHANT,
            "amount": amount_rial,
            "description": f"پرداخت سفارش ثبت شده در ارک کالا - شناسه: {str(order.id)[:8]}",
            "callback_url": callback_url,
            "metadata": {
                "mobile": mobile or "00000000000",
                "email": email
            }
        }
        
        try:
            response = requests.post(ZP_API_REQUEST, json=payload, timeout=10)
            data = response.json().get('data', {})
            
            if data and data.get('code') == 100:
                authority = data.get('authority')
                Transaction.objects.create(
                    order=order,
                    amount=order.payable_price,
                    authority=authority
                )
                return ZP_API_STARTPAY.format(authority=authority), "درخواست با موفقیت ثبت شد"
                
            return None, "درگاه پرداخت در حال حاضر پاسخگو نیست، لطفاً مجدداً تلاش کنید."
        except requests.exceptions.RequestException:
            return None, "خطا در برقراری ارتباط با سرور زرین‌پال."

    @staticmethod
    def verify_transaction(authority: str) -> Tuple[bool, str]:
        """Verify payment with ZarinPal after user returns."""
        transaction = Transaction.objects.filter(authority=authority, status=TransactionStatus.PENDING).first()
        if not transaction:
            return False, "تراکنش یافت نشد یا مهلت پرداخت به پایان رسیده است."

        amount_rial = int(transaction.amount * 10)
        payload = {
            "merchant_id": ZARINPAL_MERCHANT,
            "amount": amount_rial,
            "authority": authority
        }

        try:
            response = requests.post(ZP_API_VERIFY, json=payload, timeout=10)
            data = response.json().get('data', {})

            if data and data.get('code') in [100, 101]:
                transaction.status = TransactionStatus.SUCCESS
                transaction.ref_id = str(data.get('ref_id'))
                transaction.save()

                order = transaction.order
                order.status = OrderStatus.PAID
                order.save()

                return True, f"پرداخت با موفقیت انجام شد. کد پیگیری: {transaction.ref_id}"
            
            transaction.status = TransactionStatus.FAILED
            transaction.save()
            return False, "پرداخت توسط بانک تایید نشد."
        except requests.exceptions.RequestException:
            return False, "خطا در برقراری ارتباط جهت تایید پرداخت."