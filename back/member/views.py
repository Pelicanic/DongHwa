from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from member.authentication import CustomJWTAuthentication
from api.models import User
from .services.signup_service import (
    check_password_complexity,
    check_login_id_duplicate,
    check_nickname_duplicate,
)

#  JWT 토큰 생성 함수 (커스텀 유저 모델 대응용)
def get_tokens_for_user(user):
    refresh = RefreshToken()
    refresh["user_id"] = user.user_id  # user_id 필드를 직접 토큰에 넣어줌
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@method_decorator(csrf_exempt, name='dispatch')
class SignupView(APIView):
    def post(self, request):
        try:
            action = request.data.get('action')
            login_id = request.data.get('login_id', '')
            nickname = request.data.get('nickname', '')
            email = request.data.get('email', '')
            password = request.data.get('password', '')
            password_confirm = request.data.get('password_confirm', '')

            if action == 'check_login_id':
                if check_login_id_duplicate(login_id):
                    return Response({"success": False, "message": "이미 사용 중인 아이디입니다.", "data": None})
                return Response({"success": True, "message": "사용 가능한 아이디입니다.", "data": None})

            elif action == 'check_nickname':
                if check_nickname_duplicate(nickname):
                    return Response({"success": False, "message": "이미 사용 중인 닉네임입니다.", "data": None})
                return Response({"success": True, "message": "사용 가능한 닉네임입니다.", "data": None})

            elif action == 'check_password_strength':
                if not check_password_complexity(password):
                    return Response({"success": False, "message": "비밀번호 복잡도를 만족하지 않습니다.", "data": None})
                return Response({"success": True, "message": "비밀번호가 안전합니다.", "data": None})

            elif action == 'check_password_match':
                if password != password_confirm:
                    return Response({"success": False, "message": "비밀번호가 일치하지 않습니다.", "data": None})
                return Response({"success": True, "message": "비밀번호가 일치합니다.", "data": None})

            elif action == 'signup':
                if check_login_id_duplicate(login_id):
                    raise ValidationError("아이디 중복을 먼저 해결하세요.")
                if check_nickname_duplicate(nickname):
                    raise ValidationError("닉네임 중복을 먼저 해결하세요.")
                if password != password_confirm:
                    raise ValidationError("비밀번호가 일치하지 않습니다.")
                if not check_password_complexity(password):
                    raise ValidationError("비밀번호 복잡도를 만족하지 않습니다.")

                user = User(
                    login_id=login_id,
                    password_hash=make_password(password),
                    nickname=nickname,
                    email=email,
                )
                user.save()

                token = get_random_string(32)
                user.email_verification_token = token
                user.save()

                verification_link = request.build_absolute_uri(
                    f'/member/verify-email/?email={user.email}&token={token}'
                )

                send_mail(
                    '회원가입 이메일 인증',
                    f'인증 링크를 클릭해주세요: {verification_link}',
                    'noreply@yourdomain.com',
                    [user.email],
                )

                return Response({
                    "success": True,
                    "message": "회원가입 완료! 이메일을 확인해주세요.",
                    "data": {"user_id": user.user_id}
                })

            else:
                return Response({"success": False, "message": "잘못된 요청입니다.", "data": None}, status=400)

        except ValidationError as ve:
            return Response({"success": False, "message": str(ve), "data": None}, status=400)
        except Exception:
            return Response({"success": False, "message": "서버 오류가 발생했습니다.", "data": None}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class VerifyEmailView(APIView):
    def get(self, request):
        email = request.GET.get('email')
        token = request.GET.get('token')

        try:
            user = User.objects.get(email=email)
            if user.email_verification_token != token:
                return Response({"success": False, "message": "잘못된 토큰입니다.", "data": None}, status=400)

            user.is_active = True
            user.email_verification_token = None
            user.save()

            return Response({"success": True, "message": "이메일 인증이 완료되었습니다.", "data": None})

        except ObjectDoesNotExist:
            return Response({"success": False, "message": "잘못된 요청입니다.", "data": None}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        login_id = request.data.get('login_id')
        password = request.data.get('password')

        if not login_id or not password:
            return Response({
                "success": False,
                "message": "아이디와 비밀번호를 모두 입력해주세요.",
                "data": None
            }, status=400)

        try:
            user = User.objects.get(login_id=login_id)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "message": "아이디 또는 비밀번호가 올바르지 않습니다.",
                "data": None
            }, status=401)

        if not check_password(password, user.password_hash):
            return Response({
                "success": False,
                "message": "아이디 또는 비밀번호가 올바르지 않습니다.",
                "data": None
            }, status=401)

        if not user.is_active:
            return Response({
                "success": False,
                "message": "이메일 인증이 완료되지 않았습니다.",
                "data": None
            }, status=403)

        tokens = get_tokens_for_user(user)

        return Response({
            "success": True,
            "message": "로그인 성공! 토큰이 발급되었습니다.",
            "data": {
                "access": tokens["access"],
                "refresh": tokens["refresh"],
                "user_id": user.user_id,
                "login_id": user.login_id,
                "nickname": user.nickname
            }
        })


class LogoutView(APIView):
    def post(self, request):
        return Response({
            "success": True,
            "message": "클라이언트 측에서 토큰을 제거해 로그아웃하세요.",
            "data": None
        })


from rest_framework.views import APIView
from rest_framework.response import Response
from member.authentication import CustomJWTAuthentication

class LoginStatusView(APIView):
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request):
        user = request.user

        # user가 없거나 잘못된 경우를 직접 체크
        if not hasattr(user, "user_id"):
            return Response({
                "logged_in": False,
                "message": "로그인되지 않은 사용자입니다."
            }, status=401)

        return Response({
            "logged_in": True,
            "user_id": user.user_id,
            "nickname": user.nickname
        })