# member/urls.py
from django.urls import path
from .views import SignupView, VerifyEmailView, LoginView, LogoutView, LoginStatusView
from .custom_token_views import CustomTokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', LoginView.as_view()),       # 로그인 URL
    path('logout/', LogoutView.as_view()), # 로그아웃 URL
    path('status/', LoginStatusView.as_view(), name='login-status'), # 로그인 상태 확인 URL
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
]
