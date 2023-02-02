from django.urls import path
from . import views
app_name = 'writing'

urlpatterns = [
    path('sentence/', views.SentenceListCreateView.as_view(), name='SentenceListCreate'),
    path('sentence/<int:pk>/', views.SentenceRetrieveUpdateView.as_view(), name='RetrieveUpdate'),
    path('post/<int:sentence_id>/', views.PostListCreateView.as_view(), name='PostCreateView'),
]
