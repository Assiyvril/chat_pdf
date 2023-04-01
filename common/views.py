from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny

# from .custom_jwt import CustomJWTAuthentication
# from .serializers import CustomTokenObtainPairSerializer
from django.contrib.auth.backends import ModelBackend

from user.models import UserInfo
from user.serializers import UserInfoSerializer

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):

    permission_classes = (AllowAny,)
    # serializer_class = CustomTokenObtainPairSerializer
    # _serializer_class = CustomTokenObtainPairSerializer
    # authentication_classes = CustomJWTAuthentication

    def get_serializer_class(self):
        return TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """
        自定义登录接口, 返回 token 和 用户信息
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        password = request.data.get('password', None)
        if not password:
            return HttpResponse('密码不能为空', status=status.HTTP_400_BAD_REQUEST)
        login_type = request.data.get('login_type', None)
        if not login_type:
            return HttpResponse('login_type 不能为空', status=status.HTTP_400_BAD_REQUEST)
        if login_type == 'user':
            user_name = request.data.get('username', None)
            if not user_name:
                return HttpResponse('username 不能为空', status=status.HTTP_400_BAD_REQUEST)
            user_obj = User.objects.filter(username=user_name).first()
        elif login_type == 'email':
            email = request.data.get('email', None)
            if not email:
                return HttpResponse('email 不能为空', status=status.HTTP_400_BAD_REQUEST)
            user_obj = User.objects.filter(email=email).first()
        else:
            return HttpResponse('login_type 只能为 user 或 email', status=status.HTTP_400_BAD_REQUEST)
        if not user_obj:
            return HttpResponse('用户不存在', status=status.HTTP_400_BAD_REQUEST)
        if not user_obj.check_password(password):
            return HttpResponse('密码错误', status=status.HTTP_400_BAD_REQUEST)

        token = TokenObtainPairSerializer.get_token(user_obj)
        user_info_obj = UserInfo.objects.filter(User=user_obj).first()
        user_info_data = UserInfoSerializer(user_info_obj).data
        data = {
            'access_token': str(token.access_token),
            'refresh_token': str(token),
            'user_info': user_info_data,
        }

        return Response(data)


# class CustomTokenBackend(ModelBackend):
#
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             print('Backend', request.data)
#             if not password:
#                 raise exceptions.AuthenticationFailed('密码不能为空')
#             login_type = request.data.get('login_type', None)
#             if not login_type:
#                 raise exceptions.AuthenticationFailed('login_type 不能为空')
#             if login_type == 'user':
#                 if not username:
#                     raise exceptions.AuthenticationFailed('username 不能为空')
#                 user = User.objects.filter(username=username).first()
#             elif login_type == 'email':
#                 email = request.data.get('email', None)
#                 if not email:
#                     raise exceptions.AuthenticationFailed('email 不能为空')
#                 user = User.objects.filter(email=email).first()
#             else:
#                 raise exceptions.AuthenticationFailed('login_type 只能为 user 或 email')
#             if not user:
#                 raise exceptions.AuthenticationFailed('用户不存在')
#             if not user.check_password(password):
#                 raise exceptions.AuthenticationFailed('密码错误')
#             return user
#         except Exception as e:
#             data = {
#                 'result': 'error',
#                 'message': '登录失败, 发生未知错误{}'.format(e)
#             }
#             return None
