from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from rest_framework import status
from email.message import EmailMessage
from django.core.mail import send_mail
from .models import *
from writing.models import Subsription, Sentence
from .serializers import *
from dj_rest_auth.registration.views import SocialLoginView, LoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google import views as google_view
from django.shortcuts import redirect
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView
from dj_rest_auth.registration.views import VerifyEmailView, ConfirmEmailView
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from rest_framework.decorators import api_view, authentication_classes
from json import JSONDecodeError
from django.http import JsonResponse
import requests
from rest_framework import generics, status
from .models import *
from allauth.socialaccount.models import SocialAccount 
from rest_framework_simplejwt.authentication import JWTAuthentication
from pathlib import Path
import os, json 
from django.core.exceptions import ImproperlyConfigured 
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from dj_rest_auth.registration.serializers import VerifyEmailSerializer
from rest_framework.exceptions import MethodNotAllowed
User = get_user_model()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR, 'secrets.json')
with open(secret_file, 'r') as f: #open as로 secret.json을 열어줍니다.
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets): #예외 처리를 통해 오류 발생을 검출합니다.
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

#################################
def get_day_of_the_week(input_created_at):
    dateDict = {0: '월요일', 1:'화요일', 2:'수요일', 3:'목요일', 4:'금요일', 5:'토요일', 6:'일요일'}
    created_at = input_created_at
    day_of_the_week = dateDict[created_at.weekday()]
    return day_of_the_week

#################################
class CustomLoginView(LoginView):
    def get_response(self):
        serializer_class = self.get_response_serializer()
    
        if getattr(settings, 'REST_USE_JWT', False):
            from rest_framework_simplejwt.settings import (
                api_settings as jwt_settings,
            )
            access_token_expiration = (timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME)
            refresh_token_expiration = (timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME)
            return_expiration_times = getattr(settings, 'JWT_AUTH_RETURN_EXPIRATION', False)
            auth_httponly = getattr(settings, 'JWT_AUTH_HTTPONLY', False)

            data = {
                'user': self.user,
                'access_token': self.access_token,
            }

            if not auth_httponly:
                data['refresh_token'] = self.refresh_token
            else:
                # Wasnt sure if the serializer needed this
                data['refresh_token'] = ""

            if return_expiration_times:
                data['access_token_expiration'] = access_token_expiration
                data['refresh_token_expiration'] = refresh_token_expiration

            serializer = serializer_class(
                instance=data,
                context=self.get_serializer_context(),
            )
        elif self.token:
            serializer = serializer_class(
                instance=self.token,
                context=self.get_serializer_context(),
            )
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

        response = Response(serializer.data, status=status.HTTP_200_OK)

        if self.user.is_first:
            self.user.is_first = False
            self.user.save(update_fields=['is_first'])
    
        if getattr(settings, 'REST_USE_JWT', False):
            from dj_rest_auth.jwt_auth import set_jwt_cookies
            set_jwt_cookies(response, self.access_token, self.refresh_token)
        return response


class ReceiveConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        confirmation.confirm(self.request)
        # A React Router Route will handle the failure scenario
        return Response(status = status.HTTP_200_OK)

    def get_object(self, queryset=None):
        key = self.kwargs['key']
        email_confirmation = EmailConfirmationHMAC.from_key(key)
        if not email_confirmation:
            if queryset is None:
                queryset = self.get_queryset()
            try:
                email_confirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                # A React Router Route will handle the failure scenario
                return Response(status = status.HTTP_404_NOT_FOUND)
        return email_confirmation

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs
    
class CustomConfirmEmailView(ConfirmEmailView):
    pass

class CustomVerifyEmailView(APIView, CustomConfirmEmailView):
    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')

    def get_serializer(self, *args, **kwargs):
        return VerifyEmailSerializer(*args, **kwargs)

    def get(self, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.kwargs['key'] = serializer.validated_data['key']
        confirmation = self.get_object()
        confirmation.confirm(self.request)
        return Response({'detail': ('ok')}, status=status.HTTP_200_OK)

#################################################
####################구글##########################
#################################################
BASE_URL = 'https://port-0-osod-108dypx2ale9l8kjq.sel3.cloudtype.app/'
GOOGLE_CALLBACK_URI = BASE_URL + 'accounts/google/test/'

state = "vyv2dj"
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
# 구글 로그인

def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    #client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_id = get_secret("client_id")

    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")


def google_callback(request):
    #client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    #client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
    client_id = get_secret("client_id")
    client_secret = get_secret("client_secret")
    code = request.GET.get('code')
    # 1. 받은 코드로 구글에 access token 요청
    token_req = requests.post(f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    
    ### 1-1. json으로 변환 & 에러 부분 파싱
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    

    ### 1-2. 에러 발생 시 종료
    if error is not None:
        raise JSONDecodeError(error)
    
    ### 1-3. 성공 시 access_token 가져오기
    access_token = token_req_json.get('access_token')

    #################################################################

    # 2. 가져온 access_token으로 이메일값을 구글에 요청
    email_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code
    
    ### 2-1. 에러 발생 시 400 에러 반환
    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    
    ### 2-2. 성공 시 이메일 가져오기
    email_req_json = email_req.json()
    email = email_req_json.get('email')
    
    # return JsonResponse({'access': access_token, 'email':email})

    #################################################################

    # 3. 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = User.objects.get(email=email)
        # FK로 연결되어 있는 socialaccount 테이블에서 해당 이메일의 유저가 있는지 확인
        social_user = SocialAccount.objects.get(user=user)
        
        # 있는데 구글계정이 아니어도 에러
        if social_user.provider != 'google':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.is_first:
            user.is_first = False
            user.save(update_fields=['is_first'])

        # 이미 Google로 제대로 가입된 유저 => 로그인 & 해당 우저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
        
        accept_status = accept.status_code
        
        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

        accept_json = accept.json()
        #accept_json.pop('user', None)
        return JsonResponse(accept_json)
    
    except User.DoesNotExist:
        # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        
        accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
        
        #return JsonResponse({'err_msg': f"{accept.reason}"})
        accept_status = accept.status_code
        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        accept_json = accept.json()
        
        #accept_json.pop('user', None)
        return JsonResponse(accept_json)

    except SocialAccount.DoesNotExist:
        # User는 있는데 SocialAccount가 없을 때 (=일반회원으로 가입된 이메일일때)
        return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)       

class GetGoogleAccessView(APIView):
    def post(self, request, *args, **kwargs):
        client_id = get_secret("client_id")
        client_secret = get_secret("client_secret")
        access_token = request.data.get("access_token")
        # # Google API에 access token을 요청하는 URL 생성
        # url = "https://oauth2.googleapis.com/token"
        # data = {
        #     "code": code,
        #     "client_id": client_id,
        #     "client_secret": client_secret,
        #     "redirect_uri": GOOGLE_CALLBACK_URI,
        #     "grant_type": "authorization_code",
        # }

        # # Google API에 access token을 요청
        # response = requests.post(url, data=data)

        # # 응답에서 access token 추출
        # response_data = response.json()
        # return Response({"dd": f"{response_data}"})
        
        email_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
        email_req_status = email_req.status_code
        
        ### 2-1. 에러 발생 시 400 에러 반환
        if email_req_status != 200:
            return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
        
        ### 2-2. 성공 시 이메일 가져오기
        email_req_json = email_req.json()
        email = email_req_json.get('email')
        
        # return JsonResponse({'access': access_token, 'email':email})

        #################################################################

        # 3. 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
        try:
            # 전달받은 이메일로 등록된 유저가 있는지 탐색
            user = User.objects.get(email=email)
            # FK로 연결되어 있는 socialaccount 테이블에서 해당 이메일의 유저가 있는지 확인
            social_user = SocialAccount.objects.get(user=user)
            
            # 있는데 구글계정이 아니어도 에러
            if social_user.provider != 'google':
                return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
            
            if user.is_first:
                user.is_first = False
                user.save(update_fields=['is_first'])

            # 이미 Google로 제대로 가입된 유저 => 로그인 & 해당 우저의 jwt 발급
            data = {'access_token': access_token}
            accept = requests.post(f"{BASE_URL}google/login-test/", data=data)
            
            accept_status = accept.status_code
            
            # 뭔가 중간에 문제가 생기면 에러
            if accept_status != 200:
                return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

            accept_json = accept.json()
            #accept_json.pop('user', None)
            return JsonResponse(accept_json)
        
        except User.DoesNotExist:
            # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
            data = {'access_token': access_token}
            
            accept = requests.post(f"{BASE_URL}google/login-test/", data=data)
            
            #return JsonResponse({'err_msg': f"{accept.reason}"})
            accept_status = accept.status_code
            # 뭔가 중간에 문제가 생기면 에러
            if accept_status != 200:
                return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
            accept_json = accept.json()
            
            #accept_json.pop('user', None)
            return JsonResponse(accept_json)

        except SocialAccount.DoesNotExist:
            # User는 있는데 SocialAccount가 없을 때 (=일반회원으로 가입된 이메일일때)
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)     

class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    permission_classes = [AllowAny]


class CustomPasswordResetView(PasswordResetView):
    serializer_class = CustomPasswordResetSerializer
    html_email_template_name = 'password_reset_confirm.html'
    # extra_email_context = {
    #     'site_name': 'OSOD',
    #     'password_reset_confirm_url': 'http://127.0.0.1:8000/password/reset/confirm/uid={{ uid }}&token={{ token }}/',
    # }
    # email_template_name = 'password_reset_confirm.html'
    # extra_email_context = {
    #     'site_name': 'OSOD',
    # }
    # def post(self, request, *args, **kwargs):
    #     #data = request.data.copy()
    #     #data["email"] = request.user.email
    #     #return JsonResponse({"dd": f"{data}"})
    #     serializer = self.get_serializer(data=data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
        
    #     # Return the success message with OK HTTP status
    #     return Response(
    #         {'detail': ('Password reset e-mail has been sent.')},
    #         status=status.HTTP_200_OK,
    #     )
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data["uid"] = self.kwargs.get("uid")
        data["token"] = self.kwargs.get("token")
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': ('Password has been reset with the new password.')},
        )

# def send_email_to_valid_recipients(subject, message, recipient_list):
#     valid_recipients = []
#     invalid_recipients = []
    
#     for recipient in recipient_list:
#         try:
#             validate_email(recipient)
#             valid_recipients.append(recipient)
#         except ValidationError:
#             invalid_recipients.append(recipient)
    
#     # 유효하지 않은 이메일 주소 목록을 출력합니다.
#     if invalid_recipients:
#         print('Invalid email addresses: {}'.format(', '.join(invalid_recipients)))
    
#     # 유효한 이메일 주소 목록에 이메일을 보냅니다.
#     if valid_recipients:
#         send_mail(subject=subject, message=message, from_email=None, recipient_list=valid_recipients)


class ContactView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        sub_users = User.objects.filter(subscription=True)
        sub_unknowns = Subsription.objects.all()

        today = datetime.now().date()
        target_sentence = Sentence.objects.get(
                                created_at__year=today.year,
                                created_at__month=today.month,
                                created_at__day=today.day,
                                )

        sub_users_list = [sub_user.email for sub_user in sub_users]
        sub_unknowns_list = [sub_unknown.sub_email for sub_unknown in sub_unknowns]
        send_list = sub_users_list + sub_unknowns_list
        send_list = set(send_list)
        send_list = list(send_list)

        context = {
            'created_at': target_sentence.created_at,
            "day_of_the_week": get_day_of_the_week(target_sentence.created_at),
            'sentence': target_sentence.sentence,
            'discription': target_sentence.discription,
            'translate': target_sentence.translate,
        }

        message = render_to_string('email_template.html', context)
        subject = f"[OSOD] {get_day_of_the_week(target_sentence.created_at)}의 영작"
        to = send_list
        send_mail(
            subject = subject,
            message = "",
            from_email = None,
            recipient_list = to,
            html_message = message
        )
        return Response(status.HTTP_201_CREATED)
    
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def change_sub(request):
    user = request.user
    target = User.objects.get(id=user.id)
    if target.subscription:
        target.subscription = False
    else:
        target.subscription = True
    target.save(update_fields=['subscription'])

    return Response({
        "subscription": user.subscription,
    },status = status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def make_nickname(request):
    try:
        user = request.user
        get_nick = request.data.get('nickname')
        get_name = request.data.get('name')
        user.nickname = get_nick
        user.name = get_name
        user.save(update_fields=['nickname', 'name'])
        return Response({
            "nickname": user.nickname,
            'name': user.name
        },status = status.HTTP_200_OK)
    except:
        return Response({
            "detail": "중복이거나 형식이 잘못됐습니다.",
        },status = status.HTTP_400_BAD_REQUEST)