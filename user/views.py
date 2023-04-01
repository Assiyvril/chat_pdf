from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common_tep.jwt_login import jwt_encode_handler, jwt_payload_handler
from .serializers import UserInfoSerializer
from .models import UserInfo

User = get_user_model()


class UserInfoViewSet(viewsets.ModelViewSet):
    """
        用户信息视图
    """
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 管理员可以查看所有用户信息
        if self.request.user.is_superuser:
            return UserInfo.objects.all()
        # 匿名用户返回空
        if self.request.user.is_anonymous:
            return UserInfo.objects.none()
        # 普通用户只能查看自己的信息
        if self.request.user.is_authenticated:
            return UserInfo.objects.filter(User=self.request.user)
        else:
            return UserInfo.objects.none()

    def perform_create(self, serializer):
        serializer.save(User=self.request.user)

    @action(detail=False, methods=['get'])
    def get_user_name(self):
        return Response({'username': self.request.user.username})


class ExtraLoginView(APIView):
    """
        JWT token登录
    """
    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        data = {
            'result': 'error',
            'message': '请使用POST请求传入 username 和 password'
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        try:
            password = request.data.get('password', None)
            if not password:
                data = {
                    'result': 'error',
                    'message': 'password 不能为空'
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            login_type = request.data.get('login_type')
            if login_type == 'user':
                username = request.data.get('username', None)
                if not username:
                    data = {
                        'result': 'error',
                        'message': '当前登录形式为user_name 形式 username 不能为空'
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                user = User.objects.filter(username=username).first()
            elif login_type == 'email':
                email = request.data.get('email', None)
                if not email:
                    data = {
                        'result': 'error',
                        'message': '当前登录形式为email 形式 email 不能为空'
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                user = User.objects.filter(email=email).first()
            else:
                data = {
                    'result': 'error',
                    'message': 'login_type 只能为 user 或 email'
                }
                # user = User.objects.none()
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if not user:
                data = {
                    'result': 'error',
                    'message': '用户不存在'
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if not user.check_password(password):
                data = {
                    'result': 'error',
                    'message': '密码错误'
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            user_info_obj = UserInfo.objects.filter(User=user).first()
            user_info_data = UserInfoSerializer(user_info_obj).data
            jwt_token = jwt_encode_handler(
                jwt_payload_handler(user)
            )
            data = {
                'result': 'success',
                'message': '登录成功',
                'user_info': user_info_data,
                'token': jwt_token
            }
            return Response(data, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            data = {
                'result': 'error',
                'message': e.detail
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                'result': 'error',
                'message': '登陆失败！发生未知错误请联系管理员'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

