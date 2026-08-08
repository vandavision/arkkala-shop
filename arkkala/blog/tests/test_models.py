import pytest
from typing import Dict, Any
from django.core.exceptions import ValidationError
from blog.models import Category, Tag, Post, Comment

@pytest.mark.django_db
class TestBlogModels:

    def test_category_string_representation(self, category: Category) -> None:
        assert str(category) == 'Tech'

    def test_tag_string_representation(self, tag: Tag) -> None:
        assert str(tag) == 'Django'

    def test_post_string_representation(self, post: Post) -> None:
        assert str(post) == 'CQRS Magic'

    def test_comment_string_representation(self, comment: Comment) -> None:
        assert str(comment) == 'Comment on CQRS Magic'

    def test_comment_validation_min_length(self, post: Post) -> None:
        comment = Comment(post=post, body="Bad")
        with pytest.raises(ValidationError):
            comment.full_clean()

    def test_post_generate_json_ld(self, post: Post) -> None:
        json_ld: Dict[str, Any] = post.generate_json_ld()
        assert "@context" in json_ld
        assert "@graph" in json_ld
        assert json_ld["@graph"][0]["@type"] == "Article"
        assert json_ld["@graph"][0]["headline"] == "CQRS Magic"

    def test_post_generate_json_ld_with_faq(self, post: Post) -> None:
        post.faq_data = [{"question": "Q1", "answer": "A1"}]
        post.save()
        json_ld: Dict[str, Any] = post.generate_json_ld()
        faq_node = next((node for node in json_ld["@graph"] if node.get("@type") == "FAQPage"), None)
        assert faq_node is not None
        assert faq_node["mainEntity"][0]["name"] == "Q1"