"""
文件上传序列化器
文件保存在 UploadFile 目录下，数据库中保存文件名、文件路径、上传时间、上传者
只能接受 pdf 格式的文件
"""
import os
import random
import time

from rest_framework import serializers
from .models import UploadFile
from django.contrib.auth import get_user_model
from scripts.deal_pdf import upload_pdf
from django.conf import settings
from rest_framework.validators import UniqueTogetherValidator

PDF_BUCKET = settings.GCS_PDF_BUCKET


User = get_user_model()


class UploadFileSerializer(serializers.ModelSerializer):

    file = serializers.FileField(
        write_only=True,
        required=True,
        help_text='上传文件'
    )

    class Meta:
        model = UploadFile
        fields = ('id', 'origin_file_name', 'gcs_path', 'upload_time', 'owner')
        read_only_fields = (
            'origin_file_name', 'file_name', 'gcs_path', 'upload_time', 'owner',
            'id'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=UploadFile.objects.all(),
                fields=('file_name', 'gcs_path'),
            )
        ]

    def create(self, validated_data):
        """
        上传文件时，将文件加上时间戳和随机字符串重命名，上传至 GCS，origin_file_name, file_name, gcs_path 保存至数据库
        :param validated_data:
        :return:
        """
        file_obj = validated_data.pop('file')
        origin_file_name = file_obj.name
        new_file_name = str(int(time.time())) + str(random.randint(10000, 99999)) + '.pdf'
        try:
            gcs_path = upload_pdf(PDF_BUCKET, file_obj, new_file_name)
            if gcs_path:
                validated_data['origin_file_name'] = origin_file_name
                validated_data['file_name'] = new_file_name
                validated_data['gcs_path'] = gcs_path
                validated_data['owner'] = self.context['request'].user
                return super().create(validated_data)
            else:
                raise serializers.ValidationError('上传至GCS成功, 但未返回GCS路径！')
        except Exception as e:
            print(e)
            raise serializers.ValidationError('上传至GCS失败！')

    def validate_file(self, data):
        """
        验证文件格式
        必须是 pdf
        :return:
        """
        file_obj = self.initial_data['file']
        file_type = os.path.splitext(file_obj.name)[1]
        if file_type != '.pdf':
            raise serializers.ValidationError('文件格式错误！, 请上传 pdf 格式的文件！')
        return data
