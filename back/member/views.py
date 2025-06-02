from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from api.models import User
import re

def signup(request):
    context = {}

    if request.method == 'POST':
        action = request.POST.get('action')
        login_id = request.POST.get('login_id', '')
        nickname = request.POST.get('nickname', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        # 입력 값 유지
        context['login_id'] = login_id
        context['nickname'] = nickname
        context['email'] = email
        context['password'] = password
        context['password_confirm'] = password_confirm

        if action == 'check_login_id':
            if User.objects.filter(login_id=login_id).exists():
                context['check_login_id_msg'] = '이미 사용 중인 아이디입니다.'
            else:
                context['check_login_id_msg'] = '사용 가능한 아이디입니다.'

        elif action == 'check_nickname':
            if User.objects.filter(nickname=nickname).exists():
                context['check_nickname_msg'] = '이미 사용 중인 닉네임입니다.'
            else:
                context['check_nickname_msg'] = '사용 가능한 닉네임입니다.'

        elif action == 'check_password_strength':
            if len(password) < 8:
                context['check_password_msg'] = '비밀번호는 최소 8자 이상이어야 합니다.'
            elif not re.search(r'[a-zA-Z]', password):
                context['check_password_msg'] = '비밀번호에 영문자가 포함되어야 합니다.'
            elif not re.search(r'[0-9]', password):
                context['check_password_msg'] = '비밀번호에 숫자가 포함되어야 합니다.'
            elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                context['check_password_msg'] = '비밀번호에 특수문자가 포함되어야 합니다.'
            else:
                context['check_password_msg'] = '비밀번호가 안전합니다.'

        elif action == 'check_password_match':
            if password != password_confirm:
                context['check_password_match_msg'] = '비밀번호가 일치하지 않습니다.'
            else:
                context['check_password_match_msg'] = '비밀번호가 일치합니다.'

        elif action == 'signup':
            # 최종 회원가입 처리
            if User.objects.filter(login_id=login_id).exists():
                context['signup_msg'] = '아이디 중복을 먼저 해결하세요.'
            elif User.objects.filter(nickname=nickname).exists():
                context['signup_msg'] = '닉네임 중복을 먼저 해결하세요.'
            elif password != password_confirm:
                context['signup_msg'] = '비밀번호가 일치하지 않습니다.'
            elif len(password) < 8 or not re.search(r'[a-zA-Z]', password) or not re.search(r'[0-9]', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                context['signup_msg'] = '비밀번호 복잡도를 만족하지 않습니다.'
            else:
                user = User(
                    login_id=login_id,
                    password_hash=make_password(password),
                    nickname=nickname,
                    email=email,
                )
                user.save()

                # 이메일 인증 링크 생성 및 발송
                token = get_random_string(32)
                verification_link = request.build_absolute_uri(
                    f'/member/verify-email/?email={user.email}&token={token}'
                )

                send_mail(
                    '회원가입 이메일 인증',
                    f'인증 링크를 클릭해주세요: {verification_link}',
                    'noreply@yourdomain.com',
                    [user.email],
                )

                context['signup_msg'] = '회원가입이 완료되었습니다! 이메일을 확인해 인증을 완료해주세요.'

    return render(request, 'member/signup.html', context)

def verify_email(request):
    email = request.GET.get('email')
    token = request.GET.get('token')

    try:
        user = User.objects.get(email=email)
        # 여기서 token 검증도 필요하지만 예제에선 생략
        # user.is_active = True  # User 모델에 is_active 필드 필요!
        user.save()
        return HttpResponse('이메일 인증이 완료되었습니다!')
    except User.DoesNotExist:
        return HttpResponse('잘못된 요청입니다.')
