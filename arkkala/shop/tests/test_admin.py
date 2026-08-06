import pytest
from unittest.mock import Mock, patch
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory
from shop.admin.brand import BrandAdmin
from shop.admin.category import CategoryAdmin
from shop.admin.product import ProductAdmin, PriceHistoryAdmin
from shop.admin.interaction import CommentAdmin, QuestionAdmin
from shop.admin.inlines import ProductGalleryInline, ProductVariantInline, PriceHistoryInline
from shop.models import Brand, Category, Product, Comment, Question, ProductGallery, PriceHistory

@pytest.mark.django_db
class TestShopAdmin:
    
    def test_brand_admin_logo_preview(self, brand):
        admin_instance = BrandAdmin(Brand, AdminSite())
        assert admin_instance.logo_preview(brand) == "-"
        brand.logo = Mock(url="/media/logo.png")
        assert "<img" in admin_instance.logo_preview(brand)

    def test_category_admin_image_preview(self, category):
        admin_instance = CategoryAdmin(Category, AdminSite())
        assert admin_instance.image_preview(category) == "-"
        category.image = Mock(url="/media/cat.png")
        assert "<img" in admin_instance.image_preview(category)

    def test_product_admin_special_offer_status(self, product):
        admin_instance = ProductAdmin(Product, AdminSite())
        assert admin_instance.special_offer_status(product) == product.is_special_offer_active

    def test_price_history_admin_permissions(self):
        admin_instance = PriceHistoryAdmin(PriceHistory, AdminSite())
        req = RequestFactory().get('/')
        assert not admin_instance.has_add_permission(req)
        assert not admin_instance.has_change_permission(req)

    def test_interaction_admin_actions(self, comment, question):
        req = RequestFactory().get('/')
        req.user = Mock()
        
        comment_admin = CommentAdmin(Comment, AdminSite())
        comment_admin.message_user = Mock()
        comment_admin.approve_comments(req, Comment.objects.all())
        assert Comment.objects.first().is_approved is True
        comment_admin.reject_comments(req, Comment.objects.all())
        assert Comment.objects.first().is_approved is False

        question_admin = QuestionAdmin(Question, AdminSite())
        question_admin.message_user = Mock()
        question.is_approved = False
        question.save()
        question_admin.approve_questions(req, Question.objects.all())
        assert Question.objects.first().is_approved is True

    def test_question_admin_displays(self, question, user):
        admin_instance = QuestionAdmin(Question, AdminSite())
        
        question.answer_text = None
        assert not admin_instance.has_answer(question)
        question.answer_text = "Yes"
        assert admin_instance.has_answer(question)

        question.user = None
        question.name = "Guest"
        assert admin_instance.get_author_name(question) == "Guest"
        question.name = None
        assert admin_instance.get_author_name(question) == "مهمان"
        
        user.first_name = ""
        user.last_name = ""
        question.user = user
        assert admin_instance.get_author_name(question) == str(user.email)

    def test_inlines(self, product):
        req = RequestFactory().get('/')
        
        inline = PriceHistoryInline(Product, AdminSite())
        assert not inline.has_add_permission(req)
        
        gallery_inline = ProductGalleryInline(Product, AdminSite())
        gallery = ProductGallery(product=product)
        assert gallery_inline.image_preview(gallery) == "-"
        gallery.image = Mock(url="/media/g.png")
        assert "<img" in gallery_inline.image_preview(gallery)
        
        var_inline = ProductVariantInline(Product, AdminSite())
        db_field = Mock()
        db_field.name = "gallery_image"
        
        req.resolver_match = Mock(kwargs={})
        
        with patch('django.contrib.admin.options.InlineModelAdmin.formfield_for_foreignkey') as mock_super:
            var_inline.formfield_for_foreignkey(db_field, req)
            passed_kwargs = mock_super.call_args[1]
            assert passed_kwargs['queryset'].count() == 0

        req.resolver_match.kwargs['object_id'] = str(product.uuid)
        with patch('django.contrib.admin.options.InlineModelAdmin.formfield_for_foreignkey') as mock_super:
            var_inline.formfield_for_foreignkey(db_field, req)
            passed_kwargs = mock_super.call_args[1]
            assert passed_kwargs['queryset'].count() == 0