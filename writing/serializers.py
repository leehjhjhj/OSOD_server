from rest_framework import serializers
from .models import *
from accounts.serializers import UserDetailSerializer
from accounts.models import User


class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = ['id', 'sentence', 'discription', 'created_at', 'translate', 'is_valid']
        
class PostSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ["id", "user", "body", "sentence", "like_num", "bool_like_users", "created_at"]

class LikeUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'like_num', 'bool_like_users']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subsription
        fields = ['id', 'sub_email', 'sub_nickname']


