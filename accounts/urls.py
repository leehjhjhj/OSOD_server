from django.urls import path
from .views import *
app_name = 'accounts'


urlpatterns = [
    # 구글 소셜로그인
    path('sendemail/', ContactView.as_view(), name='ContactView'),
    path('change-sub/', change_sub, name='change_sub'),
    path('make-nickname/', make_nickname, name='make_nickname'),
    path('google/login/', GetGoogleAccessView.as_view(), name='google_login'),
    path('google/login/finish/', GoogleLogin.as_view(), name='google_login_finish'),
]
