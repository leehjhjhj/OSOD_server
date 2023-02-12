from django.urls import path
from . import views
app_name = 'writing'

urlpatterns = [
    path('sentence/', views.SentenceListCreateView.as_view(), name='SentenceListCreate'),
    path('sentence/<int:pk>/', views.SentenceRetrieveUpdateView.as_view(), name='RetrieveUpdate'),
    path('main/', views.MainSentenceView.as_view(), name='MainSentenceView'),
    ##작문 관련##
    path('post/order/<int:sentence_id>/', views.PostOrderView.as_view(), name='PostOrderView'),
    path('post/create/<int:sentence_id>/', views.PostListCreateView.as_view(), name='PostCreateView'),
    path('post/<int:pk>/', views.PostRetrieveUpdateDestroyView.as_view(), name='PostRetrieveUpdateDestroyView'),
    path('post/<int:post_id>/likes/', views.PostLikeAPIView.as_view(), name='PostLikeAPIView'),
    ##구독 관련##
    path('subscription/create/', views.SubscriptionListCreateView.as_view(), name='SubscriptionListCreateView'),
]
