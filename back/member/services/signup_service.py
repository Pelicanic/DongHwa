import re
from api.models import User

def check_login_id_duplicate(login_id):
    """아이디 중복 여부 확인"""
    return User.objects.filter(login_id=login_id).exists()

def check_nickname_duplicate(nickname):
    """닉네임 중복 여부 확인"""
    return User.objects.filter(nickname=nickname).exists()

def check_password_complexity(password):
    """
    비밀번호 복잡도 검사:
    - 8자 이상
    - 영문자 포함
    - 숫자 포함
    - 특수문자 포함
    """
    if len(password) < 8:
        return False
    if not re.search(r'[a-zA-Z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True
