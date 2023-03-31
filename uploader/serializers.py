"""
文件上传序列化器
文件保存在 UploadFile 目录下，数据库中保存文件名、文件路径、上传时间、上传者
只能接受 pdf 格式的文件
"""
import os
import random
import time

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from GPT.settings import GCS_PDF_BUCKET
from scripts.deal_pdf import upload_pdf, analyze_pdf, download_gcs_file, get_text_from_json
from .models import UploadFile

PDF_BUCKET = settings.GCS_PDF_BUCKET


User = get_user_model()


class UploadFileListSerializer(serializers.ModelSerializer):

    file = serializers.FileField(
        write_only=True,
        required=True,
        help_text='上传文件'
    )

    class Meta:
        model = UploadFile
        fields = ('id', 'file_name', 'origin_file_name', 'gcs_path', 'upload_time', 'owner',
                  'file')
        read_only_fields = (
            'origin_file_name', 'file_name', 'gcs_path', 'upload_time', 'owner',
            'id'
        )
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=UploadFile.objects.all(),
        #         fields=('file_name', 'gcs_path'),
        #     )
        # ]

    def create(self, validated_data):
        """
        上传文件时，将文件加上时间戳和随机字符串重命名，上传至 GCS, 并且解析
        origin_file_name, file_name, gcs_path, 解析结果 保存至数据库
        :param validated_data:
        :return:
        """

        file_obj = validated_data.pop('file')
        origin_file_name = file_obj.name
        new_file_name = str(int(time.time())) + str(random.randint(10000, 99999)) + '.pdf'
        try:
            print('上传文件中...')
            gcs_path = upload_pdf(
                bucket_name=PDF_BUCKET,
                source_file_obj=file_obj,
                destination_blob_name=new_file_name
            )
            if gcs_path:
                # 解析 pdf
                gcs_path = f'gs://{PDF_BUCKET}/{new_file_name}'
                analyze_result_path = f'gs://{PDF_BUCKET}/analyze_result/{new_file_name}.json'

                if analyze_pdf(gcs_path, analyze_result_path):
                    # 解析成功
                    # 下载解析结果
                    print('解析成功，十秒后开始下载解析结果...')
                    time.sleep(10)
                    print('开始下载解析结果...')
                    analyze_json_file = download_gcs_file(
                        dir_name='analyze_result',
                        gcs_source_uri=new_file_name + '.json',
                        bucket_name=GCS_PDF_BUCKET
                    )
                    print('解析结果 Json \n')
                    if analyze_json_file:
                        # 解析结果文件转换为文本
                        text = get_text_from_json(
                            json_string=analyze_json_file
                        )
                        validated_data['context'] = text
                    else:
                        raise serializers.ValidationError('解析结果文件下载失败！')
                else:
                    # 解析失败
                    raise serializers.ValidationError('您的pdf无法识别 ！')

                validated_data['origin_file_name'] = origin_file_name
                validated_data['file_name'] = new_file_name
                validated_data['gcs_path'] = gcs_path
                # 如果是未登录用户上传文件，那么 owner 为 管理员 TODO 暂定
                if not self.context['request'].user.is_authenticated:
                    validated_data['owner'] = User.objects.get(username='admin')
                else:
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


class UploadFileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadFile
        fields = '__all__'
        read_only_fields = ('id', 'file_name', 'origin_file_name', 'gcs_path',
                            'upload_time', 'owner', 'context')
