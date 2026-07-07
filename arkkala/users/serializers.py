"""
Serializers for User Authentication and Profile Management.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()



class EmailRegisterSerializer(serializers.ModelSerializer):
    """Serializer for Email/Password registration (Mode 2)."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "رمز عبور و تکرار آن مطابقت ندارند."})
        if User.objects.filter(email=attrs.get('email')).exists():
            raise serializers.ValidationError({"email": "این ایمیل قبلاً ثبت شده است."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )


class EmailLoginSerializer(TokenObtainPairSerializer):
    """Custom JWT Serializer to login using Email (Mode 2)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField(required=True)
        del self.fields[self.username_field]

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = self.get_token(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        raise serializers.ValidationError('ایمیل یا رمز عبور اشتباه است.')



class OTPSendSerializer(serializers.Serializer):
    """Serializer for requesting OTP SMS (Mode 1)."""
    phone_number = serializers.CharField(max_length=15, required=True)


class OTPVerifySerializer(serializers.Serializer):
    """Serializer for verifying OTP and generating Token (Mode 1)."""
    phone_number = serializers.CharField(max_length=15, required=True)
    code = serializers.CharField(max_length=6, required=True)



class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for viewing and updating user profile."""
    class Meta:
        model = User
        fields = ('id', 'email', 'phone_number', 'first_name', 'last_name', 'avatar', 'date_joined')
        read_only_fields = ('date_joined',)