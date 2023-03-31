from django.db import models
from uploader.models import UploadFile
from django.contrib.auth import get_user_model

"""
会话历史记录
"""

User = get_user_model()


class ChatHistory(models.Model):
    pdf_file = models.ForeignKey(
        UploadFile, on_delete=models.CASCADE, blank=False, null=False,
        verbose_name='PDF文档', help_text='PDF文档'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True,
        verbose_name='用户', help_text='用户'
    )
    history_list = models.TextField(
        blank=False, null=False, verbose_name='历史记录', help_text='历史记录'
    )
    create_time = models.DateTimeField(
        auto_now_add=True, verbose_name='创建时间', null=True, blank=True
    )
    update_time = models.DateTimeField(
        auto_now=True, verbose_name='更新时间', null=True, blank=True
    )

    class Meta:
        verbose_name = '会话历史记录'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']

    def __str__(self):
        return self.user.username + self.pdf_file.origin_file_name

