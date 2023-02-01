from rest_framework import serializers
from .models import *
from django.db import transaction
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter

class UserSerializer(RegisterSerializer):
    nickname = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=50)
    class Meta:
        model = User
        fields = ['email', 'password', 'nickname', 'name']

    def get_cleaned_data(self):
        super(UserSerializer, self).get_cleaned_data()
        return {
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'nickname': self.validated_data.get('nickname', '')
        }
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.nickname = self.cleaned_data.get('nickname')
        user.save()
        adapter.save_user(request, user, self)
        return user

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'nickname', 'name']