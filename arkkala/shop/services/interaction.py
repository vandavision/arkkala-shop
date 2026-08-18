from typing import Optional
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from shop.models.product import Product
from shop.models.interaction import Comment, Question, UserProductHistory

User = get_user_model()

class InteractionService:
    """
    Business logic for Comments, Questions and interaction history mapping.
    """
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
    def merge_guest_history_to_user(cls, user: User, guest_id: str) -> None:
        if not guest_id or not user:
            return

        guest_records = UserProductHistory.objects.filter(guest_id=guest_id, user__isnull=True)
        
        for guest_record in guest_records:
            user_record = UserProductHistory.objects.filter(user=user, product_id=guest_record.product_id).first()
            
            if user_record:
                user_record.view_count = F('view_count') + guest_record.view_count
                user_record.save(update_fields=['view_count', 'modified_at'])
                guest_record.delete()
            else:
                guest_record.user = user
                guest_record.guest_id = None
                guest_record.save(update_fields=['user', 'guest_id', 'modified_at'])