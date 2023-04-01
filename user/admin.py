from django.contrib import admin

# Register your models here.

from .models import UserInfo


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('User', 'nickname', 'integral')

