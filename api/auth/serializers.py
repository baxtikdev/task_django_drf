from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from common.users.models import Code

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "guid", "name", "phone"]


class LoginSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    guid = serializers.CharField(read_only=True)
    phone = serializers.CharField(max_length=15)

    def validate(self, data):
        phone = data['phone']
        user = User.objects.filter(phone=phone).first()
        if user is None:
            raise serializers.ValidationError("User does not exist")
        return {
            'id': user.id,
            'guid': user.guid,
            'phone': user.phone
        }

    class Meta:
        model = User
        fields = ('id', 'guid', 'phone')
        read_only_fields = ('id', 'guid', 'phone')


class ReSendCodeSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=20)

    def validate(self, data):
        phone = data['phone']
        user = User.objects.filter(phone=phone).first()
        if user is None:
            raise serializers.ValidationError("User does not exist")
        return {
            'id': user.id,
            'guid': user.guid,
            'phone': user.phone
        }

    class Meta:
        model = User
        fields = ['id', 'guid', 'phone']
        read_only_fields = ['id', 'guid', 'phone']


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True, max_length=255, required=True)


class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=6, write_only=True, required=True)
    id = serializers.IntegerField(read_only=True)
    guid = serializers.UUIDField()
    phone = serializers.CharField(max_length=15, read_only=True)
    name = serializers.CharField(max_length=100, read_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, data):
        guid = data.get('guid')
        user = User.objects.filter(guid=guid).first()
        if user is None:
            raise serializers.ValidationError("User does not exist")

        code = data.get('code')
        userCode = Code.objects.filter(user=user, number=code).first()
        if userCode is None:
            raise serializers.ValidationError("Code is not match")

        if not user.is_verified:
            user.is_verified = True
            user.save()
        if userCode.number == code:
            refresh = RefreshToken.for_user(user)
            return {
                'id': user.id,
                'guid': user.guid,
                'role': user.role,
                'phone': user.phone,
                'name': user.name,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }

    class Meta:
        model = User
        fields = ['id', 'guid', 'phone', 'name', 'access', 'refresh', 'role']
        read_only_fields = ['id', 'guid', 'phone', 'name', 'access', 'refresh', 'role']


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True, max_length=255, required=True)


class UserLoginSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    user_guid = serializers.CharField(read_only=True)
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=128, write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, data):
        phone = data['phone']
        password = data['password']

        user = authenticate(phone=phone, password=password)

        if user is None:
            raise serializers.ValidationError("User does not exist")
        try:
            refresh = RefreshToken.for_user(user)
            validation = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'user_guid': user.guid,
                'phone': user.phone,
                'role': user.role,
            }
            return validation
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

    class Meta:
        model = User
        fields = ('user_id', 'user_guid', 'phone', 'password', 'access', 'refresh', 'role')
        read_only_fields = ('user_id', 'access', 'refresh', 'role')
