from rest_framework import serializers
from .models import *
from accounts.serializers import UserDetailSerializer
from accounts.models import User
from django.utils.timezone import datetime

dateDict = {0: '월요일', 1:'화요일', 2:'수요일', 3:'목요일', 4:'금요일', 5:'토요일', 6:'일요일'}

class SentenceSerializer(serializers.ModelSerializer):
    day_of_the_week = serializers.SerializerMethodField()
    
    class Meta:
        model = Sentence
        fields = ['id', 'sentence', 'discription', 'created_at', 'translate', 'day_of_the_week']

    def get_day_of_the_week(self, obj):
        created_at = obj.created_at
        day_of_the_week = dateDict[created_at.weekday()]
        return day_of_the_week
    
class PostSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    bool_like = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "user", "body", "sentence", "like_num", "bool_like", "created_at", "unknown", "time_ago"]

    def get_bool_like(self, obj):
        request = self.context.get("request")
        if obj.like_users.filter(pk=request.user.id).exists():
            return True
        return False

    def get_time_ago(self, obj):
        now = datetime.now()
        created_at = obj.created_at
        cal_time = now - created_at
        if cal_time.seconds >= 86400:
            time_ago = f"{cal_time.seconds // 86400}일 전"
        elif cal_time.seconds >= 3600:
            time_ago = f"{cal_time.seconds // 3600}시간 전"
        elif cal_time.seconds >= 60:
            time_ago = f"{cal_time.seconds // 60}분 전"
        else:
            time_ago = f"{cal_time.seconds}초 전"
        return time_ago
  

class LikeUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'like_num']
    
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subsription
        fields = ['id', 'sub_email', 'sub_nickname']

class MypageSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    sentence = SentenceSerializer(read_only=True)
    bool_like = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ["id", "user", "body", "sentence", "like_num", "bool_like", "created_at"]

    def get_bool_like(self, obj):
        request = self.context.get("request")
        if obj.like_users.filter(pk=request.user.id).exists():
            return True
        return False