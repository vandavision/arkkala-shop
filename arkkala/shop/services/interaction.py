from typing import Optional
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from shop.models.product import Product
from shop.models.interaction import Comment, Question, UserProductHistory

User = get_user_model()

class InteractionService:
    @classmethod
    def add_comment(cls, product: Product, user: Optional[User], body: str, rating: int) -> Comment:
        return Comment.objects.create(
            product=product,
            user=user,
            body=body,
            rating=rating
        )

    @classmethod
    def add_question(cls, product: Product, text: str, user: Optional[User] = None, name: Optional[str] = None) -> Question:
        return Question.objects.create(
            product=product,
            user=user if user and user.is_authenticated else None,
            name=name if not (user and user.is_authenticated) else None,
            text=text
        )

    @classmethod
    @transaction.atomic
    def merge_guest_history_to_user(cls, user: User, guest_ids: list) -> None:
        if not guest_ids or not user:
            return

        guest_records = list(UserProductHistory.objects.filter(guest_id__in=guest_ids, user__isnull=True))

        for guest_record in guest_records:
            user_record = UserProductHistory.objects.filter(user=user, product_id=guest_record.product_id).first()

            if user_record:
                UserProductHistory.objects.filter(pk=user_record.pk).update(
                    view_count=F('view_count') + guest_record.view_count,
                    modified_at=timezone.now()
                )
                guest_record.delete()
            else:
                UserProductHistory.objects.filter(pk=guest_record.pk).update(
                    user=user,
                    guest_id=None,
                    modified_at=timezone.now()
                )

    @classmethod
    def record_product_purchase(cls, user: Optional[User], product: Product, score: int = 5) -> None:
        if not user:
            return

        history, created = UserProductHistory.objects.get_or_create(
            user=user,
            product=product,
            defaults={'view_count': score}
        )

        if not created:
            UserProductHistory.objects.filter(pk=history.pk).update(
                view_count=F('view_count') + score,
                modified_at=timezone.now()
            )