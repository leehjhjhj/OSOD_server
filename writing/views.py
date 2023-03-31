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
from django.contrib.auth import get_user_model
import random
import string
from google.cloud import translate_v2 as translate
import os
from rest_framework.permissions import IsAuthenticated
import requests
from google.oauth2 import service_account
from google.cloud import texttospeech
from rest_framework_simplejwt.authentication import JWTAuthentication
import openai
import spacy

#####################################################
today = datetime.now().date()
today_sentence = Sentence.objects.get(
                        created_at__year=today.year,
                        created_at__month=today.month,
                        created_at__day=today.day,).sentence
#####################################################
def random_nickname():
    a = random.randrange(0,10)
    b = random.randrange(0,10)
    first = ['영작하는', '영어천재', '거의 원어민', '영어마스터', '영작달인', '영어일등', '영작솜씨왕', '영문장달인', '영어고수', '영어박사']
    second = ['참새', '직박구리', '갈매기', '메추리', '비둘기', '기러기', '까마귀', '딱따구리', '뻐꾸기', '꿩']
    return f"{first[a]} {second[b]}"

def grammar_wrong_response():
    a = random.randrange(0,4)
    first = ['이런건 어때요?', '제가 한번 제안할게요!', '이게 더 자연스러울 수도 있어요!', '이게 더 나을 수도 있어요!', '이렇게 작문할 수도 있어요!']
    return f"{first[a]}"

def grammar_correct_response():
    a = random.randrange(0,4)
    first = ['완벽해요!', '틀린게 없는 문장이에요!', '너무 좋은걸요?', '완벽한 문장이에요!!', '굉장히 좋은 문장이에요!']
    return f"{first[a]}"

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

# Load the model only once
nlp = spacy.load("en_core_web_sm")

# Create a dictionary for pattern replacement
patterns = {"'ve": " have", "'ll": " will", "n't": " not", "'re": " are"}
pronouns = {"his": "ones", "her": "ones", "him": "ones", "my": "ones", "them": "ones"}
def is_pattern_used(sentence, pattern):
    if "one's" in pattern:
        for old, new in pronouns.items():
            sentence = sentence.replace(old, new)
        pattern = pattern.replace("one's", "ones")

    for old, new in patterns.items():
        sentence = sentence.replace(old, new)
        pattern = pattern.replace(old, new)
    pattern_doc = nlp(pattern.lower())

    for doc in pattern_doc:
        if doc.lemma_ == "will":
            sentence = sentence.replace("'d", " would")
        elif doc.lemma_ == "have":
            sentence = sentence.replace("'d", " had").replace("'s", " has")

    sentence_doc = nlp(sentence.lower())

    # Use a generator expression instead of a list comprehension
    new_sentence = " ".join(token.lemma_ if token.pos_ in {"AUX", "VERB"} else token.text for token in sentence_doc)
    new_pattern = " ".join(token.lemma_ if token.pos_ in {"AUX", "VERB"} else token.text for token in pattern_doc)

    return new_pattern in new_sentence
    
######################################################
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
    
class SubscriptionListCreateView(ListCreateAPIView):
    queryset = Subsription.objects.all()
    serializer_class = SubscriptionSerializer
    authentication_classes = [JWTAuthentication]
    
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    #pagination_class = SentencePagination

    def get_queryset(self):
        user_id = self.request.user.id
        today = datetime.now().date()
        return Post.objects.filter(user_id=user_id,
                                   created_at__year=today.year,
                                   created_at__month=today.month,
                                   created_at__day=today.day,).order_by('-created_at')
    
@api_view(['GET'])
def get_dates(request):
    dateDict = {0: '월요일', 1:'화요일', 2:'수요일', 3:'목요일', 4:'금요일', 5:'토요일', 6:'일요일'}
    dates = {}
    today = datetime.now().date()
    #dates['today'] = today.strftime('%y.%m.%d') + ' ' + dateDict[today.weekday()]
    for i in range(1, 8):
        date = today - timedelta(days=i)
        try: 
            sentence = Sentence.objects.get(
                                   created_at__year=date.year,
                                   created_at__month=date.month,
                                   created_at__day=date.day,).sentence
        except:
            sentence = None
        dates['today_sentence'] = today_sentence
        dates[f'{i}_days_ago'] = {
                "summary": date.strftime('%m/%d'),
                "detail": date.strftime('%Y.%m.%d') + ' ' + dateDict[date.weekday()],
                "sentence": sentence
            }
    return Response(dates)

class MypageOrderView(ListAPIView):
    serializer_class = MypageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    #pagination_class = MypagePagination

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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        posts = Post.objects.filter(user_id = user.id).order_by('-created_at')
        post_num = posts.count()
        today = datetime.now().date()
        today_study_bool = False
        continuous_cnt = 0
        prev_date = datetime.now().date()

        for post in posts:
            if post.created_at.date() == today:
                today_study_bool = True
            if post.created_at.date() == prev_date:
                continue
            if (prev_date - post.created_at.date()).days > 1:
                break
            continuous_cnt += 1
            prev_date = post.created_at.date()
        if today_study_bool:
            continuous_cnt += 1

        data = {
            "post_num" : post_num,
            "continuous_cnt": continuous_cnt,
            "liked_num": user.liked_num,
            "today_study_bool": today_study_bool,
        }
        return Response(data)

class WhatILikeView(ListAPIView):
    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.like.all().order_by('-created_at')

#######################################################################
########번역 관련########
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/innate-vigil-377910-ff58e0aebf0f.json'
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/leehyunje/Postman/OSOD/server/innate-vigil-377910-ff58e0aebf0f.json'
class TranslateView(APIView):
    def post(self, request):
        text = request.data.get('text')
        if not text:
            return Response({'translation': "번역할 문장이 없어요!"}, status=status.HTTP_200_OK)
        client = translate.Client()
        result = client.translate(text, target_language='ko')
        return Response({'translation': result['translatedText']}, status=status.HTTP_200_OK)

# from django.http import StreamingHttpResponse

# import io

# class TextToSpeechAPI(APIView):
#     def post(self, request):
#         text = request.data.get('text')
#         client = texttospeech.TextToSpeechClient()
#         synthesis_input = texttospeech.SynthesisInput(text=text)
#         voice = texttospeech.VoiceSelectionParams(
#             language_code='en-US', ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
#         )
#         audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
#         response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
#         audio_content = io.BytesIO(response.audio_content)
#         response = StreamingHttpResponse(audio_content, content_type='audio/mpeg')
#         response['Content-Disposition'] = 'attachment; filename="audio.mp3"'
#         return response
    
# #다운해서 확인하는용#
# class TextToSpeechServerdownAPI(APIView):
#     def post(self, request):
#         text = request.data.get('text')
#         client = texttospeech.TextToSpeechClient()
#         synthesis_input = texttospeech.SynthesisInput(text=text)
#         voice = texttospeech.VoiceSelectionParams(
#             language_code='en-US', ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
#         )
#         audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
#         response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
#         audio_content = io.BytesIO(response.audio_content)
        
#         # 파일로 저장
#         with open('audio.mp3', 'wb') as f:
#             f.write(audio_content.getbuffer())
        
#         # StreamingHttpResponse로 클라이언트에게 반환
#         audio_content.seek(0)
#         response = StreamingHttpResponse(audio_content, content_type='audio/mpeg')
#         response['Content-Disposition'] = 'attachment; filename="audio.mp3"'
#         return response
#####################################################################################################################



class GrammarCheckView(APIView):
    def post(self, request):
        openai.api_key = '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'
        text = request.data.get('text')
        if not text:
            return Response({'response': "", 'ai': "검사할 문장이 없어요!", 'original': "", 'bool': False}, status=status.HTTP_400_BAD_REQUEST)
        
        response = openai.Completion.create(
            model="text-davinci-003",
            #prompt=f"'{text}' correct if grammar wrong. ",
            prompt=f"'{text}' correct grammar if wrong. Preserve'{today_sentence}' ",
            temperature=0,
            max_tokens=60,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        #return Response({'response': response, 'today': today_sentence}, status=status.HTTP_200_OK)
        target_res = response.choices[0].text.strip()
        if target_res[0] == "\"":
            cut_target = target_res.strip("\"")
            if text == cut_target:
                res = cut_target
                ai = grammar_correct_response()
                bool = True
            else:
                res = cut_target
                ai = grammar_wrong_response()
                bool = False

        else:
            if text == target_res:
                res = target_res
                ai = grammar_correct_response()
                bool = True
            else:
                res = target_res
                ai = grammar_wrong_response()
                bool = False

        # if text == response.choices[0].text.strip():
        #     res = response.choices[0].text.strip()
        #     ai = grammar_correct_response()
        #     bool = True

        return Response({'response': res, 'ai': ai, 'original': text, 'bool': bool}, status=status.HTTP_200_OK)

#Correct this to standard English.
#.choices[0].text.strip()


