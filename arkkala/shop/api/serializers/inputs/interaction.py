from rest_framework import serializers

class CreateCommentInputSerializer(serializers.Serializer):
    """Serializer strictly for validating incoming Comment creation requests."""
    body = serializers.CharField(min_length=2)
    rating = serializers.IntegerField(min_value=1, max_value=5, default=5)

class CreateQuestionInputSerializer(serializers.Serializer):
    """Serializer strictly for validating incoming Question creation requests."""
    text = serializers.CharField(min_length=5)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="کاربر مهمان")