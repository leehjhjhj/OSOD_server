from .models import Feedback
from .serializers import FeedbackSerializer
from rest_framework.generics import ListCreateAPIView


class FeedbackListCreateView(ListCreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer