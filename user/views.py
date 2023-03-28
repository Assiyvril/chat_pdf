from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import UserInfoSerializer
from .models import UserInfo

User = get_user_model()


class UserInfoViewSet(viewsets.ModelViewSet):
    """
        用户信息视图
    """
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserInfo.objects.filter(User=self.request.user)

    # def perform_create(self, serializer):
    #     serializer.save(User=self.request.user)

    @action(detail=False, methods=['get'])
    def get_user_name(self):
        return Response({'username': self.request.user.username})
