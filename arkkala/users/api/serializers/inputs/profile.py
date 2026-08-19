from rest_framework import serializers
from users.models.address import UserAddress

class UserAddressInputSerializer(serializers.ModelSerializer):
    """
    Ensures safe state translations generating appropriate context strictly securely.
    """
    class Meta:
        model = UserAddress
        fields = [
            'title', 'recipient_first_name', 'recipient_last_name',
            'recipient_phone', 'province', 'city', 'postal_address',
            'postal_code', 'plaque', 'building_unit'
        ]