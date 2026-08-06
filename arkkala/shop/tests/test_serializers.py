import pytest
from unittest.mock import Mock
from django.contrib.auth.models import AnonymousUser
from shop.serializers.interaction import QuestionSerializer, CommentSerializer, UserCommentSerializer
from shop.serializers.product import ProductDetailSerializer, ProductVariantSerializer
from shop.models import Question, Comment, ProductGallery

@pytest.mark.django_db
class TestSerializersCoverage:
    def test_question_serializer_user_name(self, question, user):
        serializer = QuestionSerializer()
        
        user.first_name = ""
        user.last_name = ""
        question.user = user
        assert serializer.get_user_name(question) == "کاربر مهمان"
        
        question.user = None
        question.name = "Guest Author"
        assert serializer.get_user_name(question) == "Guest Author"

    def test_comment_serializer_user_name(self, comment, user):
        serializer = CommentSerializer()
        
        user.first_name = ""
        user.last_name = ""
        comment.user = user
        assert serializer.get_user_name(comment) == "کاربر ناشناس"
        
        comment.user = None
        assert serializer.get_user_name(comment) == "کاربر ناشناس"

    def test_user_comment_serializer_product_image(self, comment, product):
        serializer = UserCommentSerializer(context={})
        
        # In memory instance with empty gallery
        assert serializer.get_product_image(comment) is None
        
        ProductGallery.objects.create(product=product, image="test.png", is_main=True)
        assert "test.png" in serializer.get_product_image(comment)

    def test_product_detail_serializer_is_favorite(self, product, user):
        request = Mock()
        request.user = user
        
        serializer = ProductDetailSerializer(context={'request': request})
        assert serializer.get_is_favorite(product) is False
        
        product.favorites.add(user)
        assert serializer.get_is_favorite(product) is True
        
        request.user = AnonymousUser()
        assert serializer.get_is_favorite(product) is False

    def test_product_variant_serializer(self, product_variant):
        serializer = ProductVariantSerializer(instance=product_variant)
        assert "uuid" in serializer.data