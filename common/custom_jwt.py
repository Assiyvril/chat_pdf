from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
User = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        # 复写authenticate方法, 允许用户使用用户名或邮箱登录
        # 即允许 username 为空
        print('CBBBB', request.data)
        login_type = request.data.get('login_type', None)
        if not login_type:
            raise exceptions.AuthenticationFailed('login_type 不能为空')
        password = request.data.get('password', None)
        if not password:
            raise exceptions.AuthenticationFailed('password 不能为空')
        if login_type == 'user':
            username = request.data.get('username', None)
            if not username:
                raise exceptions.AuthenticationFailed('当前登录方式是username + password, username 不能为空')
            self.user = User.objects.filter(username=username).first()
        elif login_type == 'email':
            email = request.data.get('email', None)
            if not email:
                raise exceptions.AuthenticationFailed('当前登录方式是email + password, email 不能为空')
            self.user = User.objects.filter(email=email).first()
        else:
            self.user = None
            raise exceptions.AuthenticationFailed('login_type 只能为 user 或 email')
        if not self.user:
            raise exceptions.AuthenticationFailed('用户不存在')
        if not self.user.check_password(password):
            raise exceptions.AuthenticationFailed('密码错误')
        return super().authenticate(request)
