from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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

    @action(detail=False, methods=['post'])
    def register(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        if not username:
            return Response('username 不能为空', status=status.HTTP_400_BAD_REQUEST)
        # 检查用户名是否已经注册
        if User.objects.filter(username=username).exists():
            return Response('该用户名已经注册', status=status.HTTP_400_BAD_REQUEST)
        password = request.data.get('password', None)
        if not password:
            return Response('password 不能为空', status=status.HTTP_400_BAD_REQUEST)
        email = request.data.get('email', None)
        if not email:
            return Response('email 不能为空', status=status.HTTP_400_BAD_REQUEST)
        # 检查邮箱是否已经注册
        if User.objects.filter(email=email).exists():
            return Response('该邮箱已经注册', status=status.HTTP_400_BAD_REQUEST)
        first_name = request.data.get('first_name', None)
        if not first_name:
            return Response('first_name 不能为空', status=status.HTTP_400_BAD_REQUEST)
        last_name = request.data.get('last_name', None)
        if not last_name:
            return Response('last_name 不能为空', status=status.HTTP_400_BAD_REQUEST)
        nickname = request.data.get('nickname', None)
        if not nickname:
            return Response('nickname 不能为空', status=status.HTTP_400_BAD_REQUEST)
        integral = request.data.get('integral', None)
        if not integral:
            integral = 666

        user_base_obj = User.objects.create_user(
            username=username, password=password, email=email,
            first_name=first_name, last_name=last_name
        )
        user_info_obj = UserInfo.objects.create(
            user=user_base_obj, nickname=nickname, integral=integral
        )
        serializer = UserInfoSerializer(user_info_obj)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

