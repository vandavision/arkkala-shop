from typing import Optional
from rest_framework import serializers
from home.models import AboutPage

class AboutPageOutputSerializer(serializers.ModelSerializer):
    """
    Output serializer for the dynamic About Us page content.
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = AboutPage
        fields: list[str] = ['uuid', 'title', 'content', 'image_url']

    def get_image_url(self, obj: AboutPage) -> Optional[str]:
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            try:
                return request.build_absolute_uri(obj.image.url) if request else obj.image.url
            except ValueError:
                return None
        return None