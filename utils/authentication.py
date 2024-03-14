from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
 
class JwtAuthorizationAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 获取头信息token
        authorization = request.META.get('HTTP_AUTHORIZATION')
        print(authorization)
        # 校验
        try:
            valid_data = VerifyJSONWebTokenSerializer().validate({"token":authorization})
            """
            valid_data = {'token': '太长了省略一下...'
            'user': <User: xjk>
            }
            """
            user = valid_data.get("user")
            token = valid_data.get("token")
            print(user)
            if user:
                return (user, token)
            else:
                raise AuthenticationFailed("认证失败了。。。")
        except BaseException as e:
            print(e)
 