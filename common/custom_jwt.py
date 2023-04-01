from django.contrib.auth import get_user_model

from rest_framework import exceptions

from user.serializers import UserInfoSerializer

User = get_user_model()


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserInfoSerializer(user, context={'request': request}).data,
    }


# class CustomJWTAuthentication(JSONWebTokenAuthentication):
#
#     def authenticate_credentials(self, payload):
#         """
#         Returns an active user that matches the payload's user id and email.
#         """
#         username = payload.get('username')
#
#         if not username:
#             msg = 'Invalid payload.'
#             raise exceptions.AuthenticationFailed(msg)
#
#         try:
#             user = User.objects.get(username=username)
#         except Exception:
#             msg = '登录过期，请重新登录'
#             raise exceptions.AuthenticationFailed(msg)
#
#         if not user.is_active:
#             msg = '用户名不存在或被禁用.'
#             raise exceptions.AuthenticationFailed(msg)
#
#         return user
