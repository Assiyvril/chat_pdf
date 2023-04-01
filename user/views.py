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



