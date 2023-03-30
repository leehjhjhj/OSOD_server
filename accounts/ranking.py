from django.utils import timezone
from django.db.models import Count
from rest_framework import generics
from rest_framework.response import Response
from .models import User
from writing.models import Post
from .serializers import UserDetailSerializer

class UserRankingView(generics.ListAPIView):
    serializer_class = UserDetailSerializer

    def get_queryset(self):
        # 1주일 전의 날짜 및 시간
        one_week_ago = timezone.now() - timezone.timedelta(weeks=1)

        # 1주일 이내에 작성된 게시물 중 좋아요 수가 가장 많은 사용자를 가져옵니다.
        top_users = Post.objects.filter(created_at__gte=one_week_ago).values('user').annotate(total_likes=Count('like_users')).order_by('-total_likes')[:4]

        # 가져온 사용자 ID 목록
        user_ids = [user['user'] for user in top_users]

        # ID 목록에 해당하는 사용자 객체 반환
        return User.objects.filter(id__in=user_ids)