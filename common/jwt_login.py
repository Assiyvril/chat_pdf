
from django.contrib.auth import authenticate, get_user_model

from rest_framework import serializers


User = get_user_model()

# jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
# jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
# jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
# jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER

#
# class CustomJSONWebTokenSerializer(JSONWebTokenSerializer):
#     """
#     客制化 JWT 序列化器
#     """
#
#     def validate(self, attrs):
#         credentials = {
#             self.username_field: attrs.get(self.username_field),
#             'password': attrs.get('password')
#         }
#
#         if all(credentials.values()):
#             user = authenticate(**credentials)
#
#             if user:
#                 if not user.is_active:
#                     msg = '用户状态已禁用，请联系管理员'
#                     raise serializers.ValidationError(msg)
#
#                 payload = jwt_payload_handler(user)
#
#                 return {
#                     'token': jwt_encode_handler(payload),
#                     'user': user
#                 }
#             else:
#                 msg = '用户名或密码错误，请检查'
#                 raise serializers.ValidationError(msg)
#         else:
#             msg = '请输入用户名和密码。'
#             raise serializers.ValidationError(msg)
#
#
# class CustomObtainJSONWebToken(JSONWebTokenAPIView):
#     """
#     API View that receives a POST with a user's username and password.
#
#     Returns a JSON Web Token that can be used for authenticated requests.
#     """
#     serializer_class = CustomJSONWebTokenSerializer
