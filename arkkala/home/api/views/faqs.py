from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.permissions import AllowAny

from home.dependencies import home_page_reader
from home.application.queries.list_faqs import ListFAQsQuery
from home.api.serializers.outputs.faq import FAQOutputSerializer

class FAQListView(APIView):
    """
    Thin API View to retrieve active Frequently Asked Questions.
    """
    permission_classes: list = [AllowAny]

    def get(self, request: Request) -> Response:
        query = ListFAQsQuery(reader=home_page_reader)
        faqs = query.execute()
        serializer = FAQOutputSerializer(faqs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)