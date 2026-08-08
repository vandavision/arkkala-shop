import pytest
from blog.serializers.category import BlogCategorySerializer
from blog.serializers.tag import TagSerializer
from blog.serializers.comment import BlogCommentSerializer
from blog.serializers.post import PostListSerializer, PostDetailSerializer, CommentSubmissionSerializer
from blog.models import Post, Comment, Category, Tag

@pytest.mark.django_db
class TestBlogSerializers:

    def test_category_serializer(self, category: Category) -> None:
        serializer = BlogCategorySerializer(instance=category)
        assert serializer.data['title'] == 'Tech'
        assert serializer.data['slug'] == 'tech'

    def test_tag_serializer(self, tag: Tag) -> None:
        serializer = TagSerializer(instance=tag)
        assert serializer.data['title'] == 'Django'
        assert serializer.data['slug'] == 'django'

    def test_comment_serializer_user_name(self, comment: Comment) -> None:
        serializer = BlogCommentSerializer(instance=comment)
        assert serializer.data['user_name'] == 'Test User'

        comment.user = None
        comment.save()
        serializer = BlogCommentSerializer(instance=comment)
        assert serializer.data['user_name'] == 'کاربر ناشناس'

    def test_post_list_serializer(self, post: Post) -> None:
        serializer = PostListSerializer(instance=post)
        assert serializer.data['title'] == 'CQRS Magic'
        assert serializer.data['author_name'] == 'Test User'
        assert serializer.data['category']['title'] == 'Tech'

    def test_post_detail_serializer(self, post: Post, comment: Comment) -> None:
        serializer = PostDetailSerializer(instance=post)
        assert serializer.data['title'] == 'CQRS Magic'
        assert len(serializer.data['comments']) == 1
        assert serializer.data['comments'][0]['body'] == 'Great architectural insight.'

    def test_comment_submission_serializer_valid(self) -> None:
        serializer = CommentSubmissionSerializer(data={'body': 'Great post!'})
        assert serializer.is_valid() is True

    def test_comment_submission_serializer_invalid(self) -> None:
        serializer = CommentSubmissionSerializer(data={'body': ''})
        assert serializer.is_valid() is False