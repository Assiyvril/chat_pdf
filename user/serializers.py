from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import UserInfo

User = get_user_model()


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class UserInfoSerializer(ModelSerializer):
    """
        用户信息序列化
    """

    user_base_info = UserSerializer(
        source='User', read_only=True
    )

    class Meta:
        model = UserInfo
        fields = '__all__'
