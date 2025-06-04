from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from api.models import User
from .services.signup_service import (
    check_password_complexity,
    check_login_id_duplicate,
    check_nickname_duplicate,
)

class SignupView(APIView):
    def post(self, request):
        print("request.data:", request.data)
        
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

                # 이메일 인증용 토큰 생성 및 저장
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
        except Exception as e:
            return Response({"success": False, "message": "서버 오류가 발생했습니다.", "data": None}, status=500)


class VerifyEmailView(APIView):
    def get(self, request):
        email = request.GET.get('email')
        token = request.GET.get('token')

        try:
            user = User.objects.get(email=email)

            if user.email_verification_token != token:
                return Response({"success": False, "message": "잘못된 토큰입니다.", "data": None}, status=400)

            user.is_active = True
            user.email_verification_token = None  # 1회용 토큰 제거
            user.save()

            return Response({"success": True, "message": "이메일 인증이 완료되었습니다.", "data": None})

        except ObjectDoesNotExist:
            return Response({"success": False, "message": "잘못된 요청입니다.", "data": None}, status=400)
