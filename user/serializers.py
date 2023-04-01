from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import UserInfo

User = get_user_model()


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'last_login', 'username', 'first_name',
                  'last_name', 'email', 'is_active', 'date_joined')


class UserInfoSerializer(ModelSerializer):
    """
        用户信息序列化
    """

    user_base_info = UserSerializer(
        source='user', read_only=True
    )



    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = UserInfo
        fields = '__all__'

