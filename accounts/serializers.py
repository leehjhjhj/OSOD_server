from rest_framework import serializers, status
from .models import *
from django.db import transaction
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib.auth.forms import SetPasswordForm
from dj_rest_auth.serializers import PasswordResetSerializer
from django.urls import reverse
from dj_rest_auth.serializers import PasswordChangeSerializer
from rest_framework.validators import UniqueValidator
from allauth.account import app_settings as allauth_settings

class UserSerializer(RegisterSerializer):
    password1 = serializers.CharField(error_messages={'blank': '비밀번호를 설정하세요.'})
    password2 = serializers.CharField(error_messages={'blank': '비밀번호를 설정하세요.'})
    nickname = serializers.CharField(max_length=50, validators=[UniqueValidator(queryset=User.objects.all(), message='닉네임이 이미 사용중입니다.')]
                                     ,error_messages={'blank': '닉네임을 입력하세요.'})
    name = serializers.CharField(max_length=50, error_messages={'blank': '이름을 입력하세요.'})
    subscription = serializers.BooleanField(default=False)
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED, error_messages={'blank': '이메일을 입력하세요.'})

    class Meta:
        model = User
        fields = ['email', 'password', 'nickname', 'name', 'subscription']
    
    def get_cleaned_data(self):
        super(UserSerializer, self).get_cleaned_data()
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'nickname': self.validated_data.get('nickname', ''),
            'name': self.validated_data.get('name', ''),
            'subscription': self.validated_data.get('subscription', ''),
        }
    
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.nickname = self.cleaned_data.get('nickname')
        user.name = self.cleaned_data.get('name')
        user.subscription = self.cleaned_data.get('subscription')
        user.save()
        adapter.save_user(request, user, self)
        return user

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'nickname', 'name', 'liked_num', 'subscription', 'is_first']

User = get_user_model()

class CustomPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm

    set_password_form = None

    def __init__(self, *args, **kwargs):
        self.old_password_field_enabled = getattr(
            settings, 'OLD_PASSWORD_FIELD_ENABLED', True,
        )
        self.logout_on_password_change = getattr(
            settings, 'LOGOUT_ON_PASSWORD_CHANGE', True,
        )
        super().__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop('old_password')
            
        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value),
        )

        if all(invalid_password_conditions):
            err_msg = ('기존 패스워드가 일치하지 않습니다.')
            raise serializers.ValidationError(err_msg)
        return value

    def custom_validation(self, attrs):
        pass

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs,
        )

        self.custom_validation(attrs)
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(self.request, self.user)

class CustomPasswordResetSerializer(PasswordResetSerializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError({"error": "이메일이 존재하지 않습니다."})  
        return value
    
    def save(self):
        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account.forms import default_token_generator
        else:
            from django.contrib.auth.tokens import default_token_generator

        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
            'token_generator': default_token_generator,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)

class NoticeMailSerialzier(serializers.Serializer):
    subject = serializers.CharField(max_length=200)
    body_subject = serializers.CharField(max_length=200)
    body = serializers.CharField(max_length=200)