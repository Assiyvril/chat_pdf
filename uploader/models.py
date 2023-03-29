from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UploadFile(models.Model):
    origin_file_name = models.CharField(
        max_length=255, verbose_name='原始文件名', null=True, blank=True
    )
    file_name = models.CharField(
        max_length=255, verbose_name='文件名', null=True, blank=True,
        help_text='文件在 GCS 中的名称', unique=True
    )
    gcs_path = models.CharField(
        max_length=255, verbose_name='GCS路径', null=True, blank=True,
        help_text='文件在 GCS 中的路径', unique=True
    )
    upload_time = models.DateTimeField(
        auto_now_add=True, verbose_name='上传时间', null=True, blank=True
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='上传者', null=True, blank=True
    )
    context = models.TextField(
        verbose_name='解析识别后的文件内容', null=True, blank=True,
        help_text='解析识别后的文件内容'
    )

    class Meta:
        verbose_name = '上传文件'
        verbose_name_plural = verbose_name
        ordering = ['-upload_time']

    def __str__(self):
        return self.file_name
