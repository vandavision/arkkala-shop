from typing import Optional
from rest_framework import serializers
from home.models import SiteSetting

class SiteSettingOutputSerializer(serializers.ModelSerializer):
    """
    Output serializer for global site settings.
    """
    logo_url = serializers.SerializerMethodField()
    namad_1_img_url = serializers.SerializerMethodField()
    namad_2_img_url = serializers.SerializerMethodField()
    namad_3_img_url = serializers.SerializerMethodField()
    namad_4_img_url = serializers.SerializerMethodField()
    namad_5_img_url = serializers.SerializerMethodField()
    namad_6_img_url = serializers.SerializerMethodField()
    namad_7_img_url = serializers.SerializerMethodField()

    class Meta:
        model = SiteSetting
        fields: str = '__all__'

    def _get_image_url(self, image_field) -> Optional[str]:
        request = self.context.get('request')
        if image_field and hasattr(image_field, 'url'):
            try:
                return request.build_absolute_uri(image_field.url) if request else image_field.url
            except ValueError:
                return None
        return None

    def get_logo_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.logo)
    def get_namad_1_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_1_img)
    def get_namad_2_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_2_img)
    def get_namad_3_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_3_img)
    def get_namad_4_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_4_img)
    def get_namad_5_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_5_img)
    def get_namad_6_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_6_img)
    def get_namad_7_img_url(self, obj: SiteSetting) -> Optional[str]: return self._get_image_url(obj.namad_7_img)