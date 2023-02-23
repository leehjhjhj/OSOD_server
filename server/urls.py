from django.contrib import admin
from django.urls import path, include, re_path
from accounts.views import CustomPasswordResetView, CustomPasswordResetConfirmView
# urls.py
from dj_rest_auth.registration.views import VerifyEmailView, RegisterView
from dj_rest_auth.views import (
    LoginView, LogoutView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView
)
from django.views.static import serve
from . import settings
from accounts.views import ConfirmEmailView, CustomLoginView
urlpatterns = [
    path('admin/', admin.site.urls),

    # 로그인
    path('login/', CustomLoginView.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('password/change/', PasswordChangeView.as_view(), name='rest_password_change'),
    path('password/reset/', CustomPasswordResetView.as_view(), name='reset'),
    path('password/reset/confirm/uid=<int:uid>&token=<str:token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # 회원가입
    path('registration/', RegisterView.as_view(), name='rest_register'),

	path('accounts/', include('accounts.urls')),
    # 이메일 관련 필요
    path('accounts/allauth/', include('allauth.urls')),
    # make sure this url is above `dj-rest-auth`'s password-reset url
    path('dj/', include('dj_rest_auth.urls')),

    # 유효한 이메일이 유저에게 전달
    re_path(r'^account-confirm-email/$', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    # 유저가 클릭한 이메일(=링크) 확인
    re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(), name='account_confirm_email'),
    path('writing/', include('writing.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root':settings.MEDIA_ROOT}),
]
