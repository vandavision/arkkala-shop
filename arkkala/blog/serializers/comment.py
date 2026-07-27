# arkkala/blog/serializers/comment.py
from rest_framework import serializers
from blog.models.comment import Comment

class BlogCommentSerializer(serializers.ModelSerializer):
    """Serializer for Post Comments."""
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['uuid', 'user_name', 'body', 'created_at']
        
    def get_user_name(self, obj: Comment) -> str:
        """Retrieves the full name of the user or a default anonymous string."""
        if obj.user and obj.user.get_full_name():
            return obj.user.get_full_name()
        return "کاربر ناشناس"