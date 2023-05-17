
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, GenericAPIView
from .models import *
from .serializers import *
from rest_framework.response import Response

from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from rest_framework import status
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from rest_framework.views import APIView
import random
import string
from google.cloud import translate_v2 as translate
import os
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .pattern import is_pattern_used
#####################################################

#####################################################
def random_nickname():
    a = random.randrange(0,10)
    b = random.randrange(0,10)
    first = ['영작하는', '영어천재', '거의 원어민', '영어마스터', '영작달인', '영어일등', '영작솜씨왕', '영문장달인', '영어고수', '영어박사']
    second = ['참새', '직박구리', '갈매기', '메추리', '비둘기', '기러기', '까마귀', '딱따구리', '뻐꾸기', '꿩']
    return f"{first[a]} {second[b]}"

def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

@api_view(['GET'])
def get_today_postcnt(request):
    today = datetime.now().date()
    today_postcnt = Post.objects.filter(
                                created_at__year=today.year,
                                created_at__month=today.month,
                                created_at__day=today.day,
                                ).order_by('-created_at').count()
    return Response({
                "today_postcnt": today_postcnt,
                }, status = status.HTTP_200_OK)

class PostPageNumberPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('pageCnt', self.page.paginator.num_pages),
            ('curPage', self.page.number),
            ('postList', data),
        ]))

class SentencePagination(PageNumberPagination):
    page_size = 1

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('pageCnt', self.page.paginator.num_pages),
            ('curPage', self.page.number),
            ('postList', data),
        ]))
    
class MypagePagination(PageNumberPagination):
    page_size = 2

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('pageCnt', self.page.paginator.num_pages),
            ('curPage', self.page.number),
            ('postList', data),
        ]))
##########################################################

class SentenceListCreateView(ListCreateAPIView):
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer

class SentenceRetrieveUpdateView(RetrieveUpdateAPIView):
    serializer_class = SentenceSerializer

    def get_queryset(self):
        return Sentence.objects.all()

class PostListCreateView(ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        sentence_id = self.kwargs.get("sentence_id")
        if self.request.user.is_authenticated:
            user = self.request.user
            serializer.save(user=user, sentence_id=sentence_id)
        else:
            user = None
            unknown = random_nickname()
            serializer.save(user=user, sentence_id=sentence_id, unknown=unknown)

class CheckPatternView(APIView):
    def post(self, request, *args, **kwargs):
        text = request.data.get('text')
        sentence = request.data.get("sentence")
        if is_pattern_used(text, sentence):
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PostOrderView(ListAPIView):
    serializer_class = PostSerializer
    pagination_class = PostPageNumberPagination
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        #self.cmd = self.request.META.get('HTTP_CMD')
        cmd = self.kwargs.get("cmd")
        sentence_id = self.kwargs.get("sentence_id")
        page = self.kwargs.get("page")
        user_id = self.request.user.id
        if cmd == "latest":
            return Post.objects.filter(sentence_id=sentence_id).order_by('-created_at')
        elif cmd == "likes":
            return Post.objects.filter(sentence_id=sentence_id).order_by('-like_num')
        elif cmd == "my":
            return Post.objects.filter(sentence_id=sentence_id, user_id=user_id).order_by('-created_at')


class PostRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

class PostLikeAPIView(GenericAPIView):
    serializer_class = LikeUsersSerializer
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        post_id = self.kwargs.get("post_id")
        post = Post.objects.get(pk=post_id)
        post_user = post.user

        if post.like_users.filter(pk=user.id).exists():
            post.like_users.remove(user)
            if post.user:
                post.user.liked_num -= 1
                post_user.save(update_fields=['liked_num'])
            post.like_num = post.like_users.count()
            post.save(update_fields=['like_num'])
            bool_like = False
            return Response(
                {
                "bool_like": bool_like,
                "like_num": post.like_num,
                },
                status = status.HTTP_200_OK
            )
        else:
            post.like_users.add(user)
            if post.user:
                post.user.liked_num += 1
                post_user.save(update_fields=['liked_num'])
            post.like_num = post.like_users.count()
            post.save(update_fields=['like_num'])
            bool_like = True
            return Response(
                {
                "bool_like": bool_like,
                "like_num": post.like_num,
                },
                status = status.HTTP_200_OK
            )
        
class MainSentenceView(ListAPIView):
    serializer_class = SentenceSerializer
    pagination_class = SentencePagination

    def get_queryset(self):
        today = datetime.now().date()
        return Sentence.objects.filter(
                                created_at__year=today.year,
                                created_at__month=today.month,
                                created_at__day=today.day,
                                # created_at__month=2,
                                # created_at__day=27,
                                ).order_by('-created_at')
    

    
########번역 관련########
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/innate-vigil-377910-ff58e0aebf0f.json'
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/leehyunje/Postman/OSOD/server/innate-vigil-377910-ff58e0aebf0f.json'


from google.auth.credentials import Credentials


class TranslateView(APIView):
    def post(self, request):
        text = request.data.get('text')
        if not text:
            return Response({'translation': "번역할 문장이 없어요!"}, status=status.HTTP_200_OK)
        #client = translate.Client()
        client = translate.Client()
        result = client.translate(text, target_language='ko')
        return Response({'translation': result['translatedText']}, status=status.HTTP_200_OK)
