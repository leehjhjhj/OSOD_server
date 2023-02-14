from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, GenericAPIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from rest_framework import status
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from rest_framework.views import APIView

######################################################
class PostPageNumberPagination(PageNumberPagination):
    page_size = 4

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

    def perform_create(self, serializer):    
        sentence_id = self.kwargs.get("sentence_id")
        user_id = self.request.user.id
        serializer.save(user_id = user_id, sentence_id = sentence_id)


class PostOrderView(ListAPIView):
    serializer_class = PostSerializer
    pagination_class = PostPageNumberPagination

    def get_queryset(self):
        #self.cmd = self.request.META.get('HTTP_CMD')
        cmd = self.kwargs.get("cmd")
        sentence_id = self.kwargs.get("sentence_id")
        user_id = self.request.user.id
        if cmd == "latest":
            return Post.objects.filter(sentence_id=sentence_id).order_by('-created_at')
        elif cmd == "likes":
            return Post.objects.filter(sentence_id=sentence_id).order_by('-like_num')
        elif cmd == "my":
            return Post.objects.filter(sentence_id=sentence_id, user_id=user_id).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PostRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.all()

class PostLikeAPIView(GenericAPIView):
    serializer_class = LikeUsersSerializer

    def get(self, request, *args, **kwargs):
        user = self.request.user
        post_id = self.kwargs.get("post_id")
        post = Post.objects.get(pk=post_id)

        if post.like_users.filter(pk=user.id).exists():
            post.like_users.remove(user)
            post.like_num = post.like_users.count()
            bool_like = False
            return Response(
                {
                "bool_like": bool_like,
                "like_num": post.like_num
                },
                status = status.HTTP_200_OK
            )
        else:
            post.like_users.add(user)
            post.like_num = post.like_users.count()
            bool_like = True
            return Response(
                {
                "bool_like": bool_like,
                "like_num": post.like_num
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
                                ).order_by('-created_at')
    
class SubscriptionListCreateView(ListCreateAPIView):
    queryset = Subsription.objects.all()
    serializer_class = SubscriptionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if User.objects.filter(email = serializer.validated_data.get('sub_email')).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

###########################마이 페이지###########################################
class MypageTodayIWroteView(ListAPIView):
    serializer_class = MypageSerializer
    pagination_class = SentencePagination

    def get_queryset(self):
        user_id = self.request.user.id
        today = datetime.now().date()
        return Post.objects.filter(user_id=user_id,
                                   created_at__year=today.year,
                                   created_at__month=today.month,
                                   created_at__day=today.day,).order_by('-created_at')
    
@api_view(['GET'])
def get_dates(request):
    dates = {}
    today = datetime.now().date()
    dates['today'] = today.strftime('%m/%d')
    for i in range(1, 8):
        date = today - timedelta(days=i)
        dates[f'{i}_days_ago'] = date.strftime('%m/%d')
    return Response(dates)

class MypageOrderView(ListAPIView):
    serializer_class = MypageSerializer
    pagination_class = MypagePagination

    def get_queryset(self):
        date = self.kwargs.get("date")
        month, day = date.split("&")
        user_id = self.request.user.id
        return Post.objects.filter(created_at__year='2023',
                                   created_at__month=month,
                                   created_at__day=day,
                                   user_id=user_id).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class MypageUserDetailView(APIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        posts = Post.objects.filter(user_id = user.id).count()
        today = datetime.now().date()
        sign_in_days = (today - user.date_joined.date()).days
        data = {
            "post_num" : posts,
            "sign_in_days": sign_in_days
        }
        return Response(data)

class WhatILikeView(ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        return user.like.all().order_by('-created_at')

#######################################################################