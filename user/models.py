from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserInfo(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name='用户'
    )
    nickname = models.CharField(max_length=20, verbose_name='昵称')
    integral = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='积分'
    )

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name
