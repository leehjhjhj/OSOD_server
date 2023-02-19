from django.urls import path
from . import views
app_name = 'writing'

urlpatterns = [
    ##구문 관련##
    path('sentence/', views.SentenceListCreateView.as_view(), name='SentenceListCreate'),
    path('sentence/<int:pk>/', views.SentenceRetrieveUpdateView.as_view(), name='RetrieveUpdate'),
    path('main/', views.MainSentenceView.as_view(), name='MainSentenceView'),
    ##작문 관련##
    path('post/order/<int:sentence_id>/query=<str:cmd>/', views.PostOrderView.as_view(), name='PostOrderView'),
    path('post/create/<int:sentence_id>/', views.PostListCreateView.as_view(), name='PostCreateView'),
    path('post/<int:pk>/', views.PostRetrieveUpdateDestroyView.as_view(), name='PostRetrieveUpdateDestroyView'),
    path('post/<int:post_id>/likes/', views.PostLikeAPIView.as_view(), name='PostLikeAPIView'),
    path('post/todaypostcnt/', views.get_today_postcnt, name='get_today_postcnt'),
    ##구독 관련##
    path('subscription/create/', views.SubscriptionListCreateView.as_view(), name='SubscriptionListCreateView'),
    ##기타 기능##
    path('translate/', views.TranslateView.as_view()),
    ##마이페이지 관련##
    path('mypage/today/', views.MypageTodayIWroteView.as_view(), name='today'),
    path('mypage/get_dates/', views.get_dates, name='get_dates'),
    path('mypage/query=<str:date>/', views.MypageOrderView.as_view(), name='MypageOrderView'),
    path('mypage/userdetail/', views.MypageUserDetailView.as_view(), name='userdetail'),
    path('mypage/ilike/', views.WhatILikeView.as_view(), name='WhatILikeView'),
]
