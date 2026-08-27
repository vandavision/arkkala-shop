from rest_framework import serializers
from home.models import FAQ

class FAQOutputSerializer(serializers.ModelSerializer):
    """
    Output serializer for active FAQs.
    """
    class Meta:
        model = FAQ
        fields: list[str] = ['uuid', 'question', 'answer', 'order']