from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import AllowAny

from home.dependencies import home_page_reader
from home.application.queries.get_about_page import GetAboutPageQuery
from home.api.serializers.outputs.about import AboutPageOutputSerializer

class AboutPageDetailView(APIView):
    """
    Thin API View mapping the GetAboutPageQuery execution.
    """
    permission_classes: list = [AllowAny]

    def get(self, request: Request) -> Response:
        query = GetAboutPageQuery(reader=home_page_reader)
        about_content = query.execute()
        
        if not about_content:
            return Response(
                {
                    "title": "درباره ما",
                    "content": "محتوایی برای این صفحه ثبت نشده است.",
                    "image_url": None
                },
                status=status.HTTP_200_OK
            )
            
        serializer = AboutPageOutputSerializer(about_content, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)