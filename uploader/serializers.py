"""
文件上传序列化器
文件保存在 UploadFile 目录下，数据库中保存文件名、文件路径、上传时间、上传者
只能接受 pdf 格式的文件
"""
import os

from rest_framework import serializers
from .models import UploadFile
from django.contrib.auth import get_user_model


User = get_user_model()


class UploadFileSerializer(serializers.ModelSerializer):

    file = serializers.FileField(write_only=True)

    class Meta:
        model = UploadFile
        fields = '__all__'
        read_only_fields = (
            'origin_file_name', 'file_name', 'gcs_path', 'upload_time', 'owner'
        )
