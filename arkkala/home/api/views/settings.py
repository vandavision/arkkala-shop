from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import AllowAny

from home.dependencies import home_page_reader
from home.application.queries.get_site_settings import GetSiteSettingsQuery
from home.api.serializers.outputs.settings import SiteSettingOutputSerializer

class SiteSettingView(APIView):
    """
    Thin API View for retrieving the global site settings.
    """
    permission_classes: list = [AllowAny]

    def get(self, request: Request) -> Response:
        query = GetSiteSettingsQuery(reader=home_page_reader)
        setting = query.execute()
        serializer = SiteSettingOutputSerializer(setting, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)