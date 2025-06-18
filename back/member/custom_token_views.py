from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import User
from rest_framework.response import Response
from rest_framework import status

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh_token = RefreshToken(attrs['refresh'])
        
        # 토큰에서 user_id 가져오기
        try:
            user_id = refresh_token.get('user_id')
            # api.User 모델로 사용자 확인
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise InvalidToken('User not found')
        except Exception as e:
            raise InvalidToken(f'Token validation error: {str(e)}')
        
        # 새로운 access token 생성
        data = {'access': str(refresh_token.access_token)}
        
        # refresh token 회전 설정이 활성화된 경우
        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # 기존 refresh token을 블랙리스트에 추가
                    refresh_token.blacklist()
                except AttributeError:
                    # 블랙리스트 앱이 설치되지 않은 경우 무시
                    pass
            
            # 새로운 refresh token 생성
            refresh_token.set_jti()
            refresh_token.set_exp()
            refresh_token.set_iat()
            
            data['refresh'] = str(refresh_token)
        
        return data

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'detail': f'Token refresh failed: {str(e)}'},
                status=status.HTTP_401_UNAUTHORIZED
            )
