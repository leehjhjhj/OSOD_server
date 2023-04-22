
from rest_framework.response import Response
from writing.models import Post
from rest_framework.views import APIView
from datetime import datetime, timedelta
from rest_framework import status

class WeekIsWritingView(APIView):
    def get(self, *args, **kwargs):
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        user = self.request.user
        result = {str((start_of_week + timedelta(days=i)).date()): 0 for i in range(7)}
        
        post_dates = Post.objects.filter(user_id=user.id, created_at__range=[start_of_week, end_of_week]).only('created_at')

        if post_dates.exists():
            for post in post_dates:
                date = str(post.created_at.date())
                result[date] = 1
        else:
            return Response({'week_is_writing': result}, status=status.HTTP_200_OK)
        return Response({'week_is_writing': result}, status=status.HTTP_200_OK)