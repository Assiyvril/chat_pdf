from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .serializers import UploadFileSerializer
from .models import UploadFile


class UploadFileViewSet(viewsets.ModelViewSet):
    """
    文件上传视图
    """
    queryset = UploadFile.objects.all()
    serializer_class = UploadFileSerializer

    def get_queryset(self):
        return UploadFile.objects.filter(upload_user=self.request.user)
