from django.contrib import admin
from django.urls import path, include, re_path
'''
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('writing/', include('writing.urls')),
    path('accounts/', include('dj_rest_auth.urls')),
    path('accounts/register/', include('dj_rest_auth.registration.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
]
'''
# urls.py
from dj_rest_auth.registration.views import VerifyEmailView, RegisterView
from dj_rest_auth.views import (
    LoginView, LogoutView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView
)

from accounts.views import ConfirmEmailView

urlpatterns = [
    path('admin/', admin.site.urls),

    # 로그인
    path('rest-auth/login', LoginView.as_view(), name='rest_login'),
    path('rest-auth/logout', LogoutView.as_view(), name='rest_logout'),
    path('rest-auth/password/change', PasswordChangeView.as_view(), name='rest_password_change'),
    # 회원가입
    path('rest-auth/registration', RegisterView.as_view(), name='rest_register'),
	path('accounts/', include('accounts.urls')),
    # 이메일 관련 필요
    path('accounts/allauth/', include('allauth.urls')),
    path('dj/', include('dj_rest_auth.urls')),
    # 유효한 이메일이 유저에게 전달
    re_path(r'^account-confirm-email/$', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    # 유저가 클릭한 이메일(=링크) 확인
    re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(), name='account_confirm_email'),
]