from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import status
from rest_framework_simplejwt import exceptions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from .serializers import CustomTokenObtainPairSerializer
from django.contrib.auth.backends import ModelBackend


User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):

    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            print('Backend', request.data)
            if not password:
                raise exceptions.AuthenticationFailed('密码不能为空')
            login_type = request.data.get('login_type', None)
            if not login_type:
                raise exceptions.AuthenticationFailed('login_type 不能为空')
            if login_type == 'user':
                if not username:
                    raise exceptions.AuthenticationFailed('username 不能为空')
                user = User.objects.filter(username=username).first()
            elif login_type == 'email':
                email = request.data.get('email', None)
                if not email:
                    raise exceptions.AuthenticationFailed('email 不能为空')
                user = User.objects.filter(email=email).first()
            else:
                raise exceptions.AuthenticationFailed('login_type 只能为 user 或 email')
            if not user:
                raise exceptions.AuthenticationFailed('用户不存在')
            if not user.check_password(password):
                raise exceptions.AuthenticationFailed('密码错误')
            return user
        except Exception as e:
            data = {
                'result': 'error',
                'message': '登录失败, 发生未知错误{}'.format(e)
            }
            return None
