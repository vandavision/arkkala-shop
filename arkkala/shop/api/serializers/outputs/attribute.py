from rest_framework import serializers
from shop.models.attribute import AttributeValue

class AttributeValueSerializer(serializers.ModelSerializer):
    """Outputs attribute values contextually."""
    attribute_name = serializers.CharField(source='attribute.title')

    class Meta:
        model = AttributeValue
        fields = ['uuid', 'attribute_name', 'value']