# from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User
# from rest_framework import authentication
# from rest_framework import exceptions
#
#
# user = get_user_model()
#
#
# class CustomAuthentication(authentication.BaseAuthentication):
#
#     def authenticate(self, request):
#         username = request.data.get('username', None)
#         password = request.data.get('password', None)
#         if not username or not password:
#             raise exceptions.AuthenticationFailed('111111 用户名或密码不能为空')
#         user = User.objects.filter(username=username).first()
#         if not user:
#             raise exceptions.AuthenticationFailed('用户不存在')
#         if not user.check_password(password):
#             raise exceptions.AuthenticationFailed('密码错误')
#         return (user, None)
