from typing import Dict, Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import AllowAny

from home.dependencies import home_page_reader, home_cache_backend
from home.application.queries.get_home_page_data import GetHomePageDataQuery
from home.api.serializers.outputs.home_data import HomePageDataOutputSerializer

class HomePageDataView(APIView):
    """
    Thin API View mapping the GetHomePageDataQuery execution to output schema.
    """
    permission_classes: list = [AllowAny]

    def get(self, request: Request) -> Response:
        cached_data: Dict[str, Any] | None = home_cache_backend.get_home_page_data()
        
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        query = GetHomePageDataQuery(reader=home_page_reader)
        raw_data = query.execute()

        serializer = HomePageDataOutputSerializer(raw_data, context={'request': request})
        serialized_data = serializer.data

        home_cache_backend.set_home_page_data(serialized_data)
        
        return Response(serialized_data, status=status.HTTP_200_OK)