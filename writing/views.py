from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, GenericAPIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class SentenceListCreateView(ListCreateAPIView):
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer

class SentenceRetrieveUpdateView(RetrieveUpdateAPIView):
    serializer_class = SentenceSerializer

    def get_queryset(self):
        #pk = self.kwargs.get('pk')
        return Sentence.objects.all()

class PostListCreateView(ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        sentence_id = self.kwargs.get("sentence_id")
        user_id = self.request.user.id
        #user = get_object_or_404(User, pk=user_id)
        serializer.save(user_id = user_id, sentence_id = sentence_id)

#class PostAPIView(GenericAPIView):

