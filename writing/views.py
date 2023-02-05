from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, GenericAPIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from django.db.models.query import QuerySet
from rest_framework import status

class PostPageNumberPagination(PageNumberPagination):
    page_size = 4

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('pageCnt', self.page.paginator.num_pages),
            ('curPage', self.page.number),
            ('postList', data),
        ]))

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
        self.cmd = self.request.META.get('HTTP_CMD')
        sentence_id = self.kwargs.get("sentence_id")
        user_id = self.request.user.id
        if self.cmd == "latest":
            return Post.objects.filter(sentence_id=sentence_id).order_by('-created_at')
        elif self.cmd == "likes":
            return Post.objects.filter(sentence_id=sentence_id).order_by('-like_num')
        elif self.cmd == "my":
            return Post.objects.filter(sentence_id=sentence_id, user_id=user_id).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        for post in queryset:
            if post.like_users.filter(pk=self.request.user.id).exists():
                post.bool_like_users = True
            else:
                post.bool_like_users = False
            post.save(update_fields=['bool_like_users'])
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
            post.bool_like_users = False
            post.save(update_fields=['like_num', 'bool_like_users'])
            serializer = LikeUsersSerializer(post)
            return Response(
                serializer.data,
                status = status.HTTP_200_OK
            )
        else:
            post.like_users.add(user)
            post.like_num = post.like_users.count()
            post.bool_like_users = True
            post.save(update_fields=['like_num', 'bool_like_users'])
            serializer = LikeUsersSerializer(post)
            return Response(
                serializer.data,
                status = status.HTTP_200_OK
            )