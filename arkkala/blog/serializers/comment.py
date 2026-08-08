from rest_framework import serializers
from blog.models.comment import Comment

class BlogCommentSerializer(serializers.ModelSerializer):
    """
    Resolves comment instances eliminating inner structural leaks robustly.
    """
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields: list = ['uuid', 'user_name', 'body', 'created_at']
        
    def get_user_name(self, obj: Comment) -> str:
        """
        Dynamically extracts and evaluates identifier accurately omitting null references.
        """
        if obj.user and obj.user.get_full_name():
            return obj.user.get_full_name()
        return "کاربر ناشناس"