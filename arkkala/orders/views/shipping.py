from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from orders.models import ShippingMethod
from orders.serializers.shipping import ShippingMethodSerializer


class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """List available shipping methods."""
    queryset = ShippingMethod.objects.filter(is_active=True)
    serializer_class = ShippingMethodSerializer
    permission_classes = [AllowAny]