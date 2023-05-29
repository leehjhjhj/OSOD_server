from django.urls import path
from .views import *
from .grammar import *
from .mypage import *
from .subscription import SubscriptionListCreateView

app_name = 'writing'

urlpatterns = [
    ##구문 관련##
    path('sentence/', SentenceListCreateView.as_view(), name='SentenceListCreate'),
    path('sentence/<int:pk>/', SentenceRetrieveUpdateView.as_view(), name='RetrieveUpdate'),
    path('main/', MainSentenceView.as_view(), name='MainSentenceView'),
    ##작문 관련##
    path('post/order/<int:sentence_id>/query=<str:cmd>/', PostOrderView.as_view(), name='PostOrderView'),
    path('post/create/<int:sentence_id>/', PostListCreateView.as_view(), name='PostCreateView'),
    path('post/<int:pk>/', PostRetrieveUpdateDestroyView.as_view(), name='PostRetrieveUpdateDestroyView'),
    path('post/<int:post_id>/likes/', PostLikeAPIView.as_view(), name='PostLikeAPIView'),
    path('post/todaypostcnt/', get_today_postcnt, name='get_today_postcnt'),
    ##구독 관련##
    path('subscription/create/', SubscriptionListCreateView.as_view(), name='SubscriptionListCreateView'),
    ##기타 기능##
    path('translate/', TranslateView.as_view()),
    # path('text-to-speech/', views.TextToSpeechAPI.as_view()),
    # path('text-to-speech-server/', views.TextToSpeechServerdownAPI.as_view()),
    path('grammar-check/', GrammarCheckView.as_view(), name='grammar'),
    path('pattern-check/', CheckPatternView.as_view(), name='Pattern'),
    ##마이페이지 관련##
    path('mypage/today/', MypageTodayIWroteView.as_view(), name='today'),
    path('mypage/get_dates/', get_dates, name='get_dates'),
    path('mypage/query=<str:date>/', MypageOrderView.as_view(), name='MypageOrderView'),
    path('mypage/userdetail/', MypageUserDetailView.as_view(), name='userdetail'),
    path('mypage/ilike/', WhatILikeView.as_view(), name='WhatILikeView'),
    path('mypage/week/', WeekIsWritingView.as_view(), name='week_is_writing'),
]
