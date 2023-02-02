from rest_framework import serializers
from .models import *
from accounts.serializers import UserDetailSerializer
from accounts.models import User


class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = ['sentence', 'discription', 'created_at']
        
class PostSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()
    class Meta:
        model = Post
        fields = ["user", "sentence", "like_num"]





