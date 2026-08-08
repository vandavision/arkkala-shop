from rest_framework import serializers

class CommentSubmissionSerializer(serializers.Serializer):
    body = serializers.CharField(required=True, allow_blank=False)