"""
自定义登录序列化器
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import exceptions
from django.contrib.auth import get_user_model

from user.models import UserInfo
from user.serializers import UserInfoSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        # 复写validate方法, 允许用户使用用户名或邮箱登录
        # 即允许 username 为空
        print(self.context['request'].data)
        login_type = self.context['request'].data.get('login_type', None)
        if not login_type:
            raise exceptions.AuthenticationFailed('login_type 不能为空')
        password = self.context['request'].data.get('password', None)
        if not password:
            raise exceptions.AuthenticationFailed('password 不能为空')
        if login_type == 'user':
            username = self.context['request'].data.get('username', None)
            if not username:
                raise exceptions.AuthenticationFailed('当前登录方式是username + password, username 不能为空')
            self.user = User.objects.filter(username=username).first()
        elif login_type == 'email':
            email = self.context['request'].data.get('email', None)
            if not email:
                raise exceptions.AuthenticationFailed('当前登录方式是email + password, email 不能为空')
            self.user = User.objects.filter(email=email).first()
        else:
            self.user = None
            raise exceptions.AuthenticationFailed('login_type 只能为 user 或 email')
        if not self.user:
            raise exceptions.AuthenticationFailed('用户不存在')
        if not self.user.check_password(password):
            raise exceptions.AuthenticationFailed('密码错误')

        # data = super().validate(attrs)
        data = {}
        print(self.user)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        user_info_obj = UserInfo.objects.filter(User=self.user).first()
        if user_info_obj:
            user_info_data = UserInfoSerializer(user_info_obj).data
        else:
            user_info_data = {}
        data['user_info'] = user_info_data
        return data


