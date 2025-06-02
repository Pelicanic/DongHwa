# member/forms.py
import re
from django import forms
from api.models import User

class SignUpForm(forms.Form):
    login_id = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    nickname = forms.CharField(max_length=50)
    email = forms.EmailField()

    def clean_login_id(self):
        login_id = self.cleaned_data['login_id']
        if User.objects.filter(login_id=login_id).exists():
            raise forms.ValidationError('이미 사용 중인 아이디입니다.')
        return login_id

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        if User.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError('이미 사용 중인 닉네임입니다.')
        return nickname

    def clean_password(self):
        password = self.cleaned_data['password']
        # 영어, 숫자, 특수문자 포함 체크
        if not re.search(r'[a-zA-Z]', password):
            raise forms.ValidationError('비밀번호에 영문자가 포함되어야 합니다.')
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError('비밀번호에 숫자가 포함되어야 합니다.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError('비밀번호에 특수문자가 포함되어야 합니다.')
        if len(password) < 8:
            raise forms.ValidationError('비밀번호는 최소 8자 이상이어야 합니다.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('비밀번호와 비밀번호 확인이 일치하지 않습니다.')
