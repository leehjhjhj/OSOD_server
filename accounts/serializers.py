from rest_framework import serializers
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

class UserSerializer(RegisterSerializer):
    nickname = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=50)
    subscription = serializers.BooleanField(default=False)

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
    