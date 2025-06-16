# back/member/authentication.py

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from api.models import User

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # ✅ Authorization 헤더가 없는 경우 인증을 생략함
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

    def get_user(self, validated_token):
        try:
            # 🔍 user_id 추출
            user_id = validated_token.get("user_id")
            print(f"[🔍 인증] 토큰에서 추출한 user_id: {user_id}")

            # ✅ DB에서 유저 조회
            user = User.objects.get(user_id=user_id)

            # ✅ IsAuthenticated 권한 검사를 통과시키기 위해 수동으로 속성을 설정합니다.
            user.is_authenticated = True
            
            print(f"[✅ 인증] 유저 조회 성공: {user.login_id} (ID: {user.user_id})")
            return user

        except User.DoesNotExist:
            print(f"[❌ 인증] user_id={user_id} 해당 유저를 DB에서 찾을 수 없습니다.")
            raise InvalidToken({
                "detail": "User not found",
                "code": "user_not_found"
            })

        except Exception as e:
            print(f"[‼️ 예외] 인증 처리 중 예외 발생: {str(e)}")
            raise InvalidToken({
                "detail": f"Unexpected error: {str(e)}",
                "code": "unexpected_error"
            })