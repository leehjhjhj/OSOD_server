from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import *
from django.template.loader import render_to_string
from rest_framework import generics, status
from writing.models import Subsription, Sentence
from rest_framework.response import Response
from django.core.mail import EmailMessage
from datetime import datetime, timedelta
from rest_framework.generics import GenericAPIView
from .serializers import NoticeMailSerialzier
from django.utils.safestring import mark_safe


def get_day_of_the_week(input_created_at):
    dateDict = {0: '월요일', 1:'화요일', 2:'수요일', 3:'목요일', 4:'금요일', 5:'토요일', 6:'일요일'}
    created_at = input_created_at
    day_of_the_week = dateDict[created_at.weekday()]
    return day_of_the_week

class SubMailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        sub_users = User.objects.filter(subscription=True).values('email')
        sub_unknowns = Subsription.objects.values('sub_email')

        today = datetime.now().date()
        target_sentence = Sentence.objects.get(
            created_at__year=today.year,
            created_at__month=today.month,
            created_at__day=today.day,
        )

        #send_list = [sub_user['email'] for sub_user in sub_users] + [sub_unknown['sub_email'] for sub_unknown in sub_unknowns]
        send_list = list(dict.fromkeys(send_list))
        send_list = ["201802977@hufs.ac.kr", "tsukiakarii@naver.com", "genioustic@naver.com"]
        context = {
            'created_at': target_sentence.created_at,
            "day_of_the_week": get_day_of_the_week(target_sentence.created_at),
            'sentence': target_sentence.sentence,
            'discription': target_sentence.discription,
            'translate': target_sentence.translate,
        }

        message = render_to_string('email_template.html', context)
        subject = f"[OSOD] {get_day_of_the_week(target_sentence.created_at)}의 영작"

        email = EmailMessage(
                subject = subject,
                body = message,
                from_email = 'OSOD <officialosod@gmail.com>',
                bcc = send_list,
                reply_to=['OSOD <officialosod@gmail.com>'],
            )
        email.content_subtype = 'html'
        email.send()
        return Response(status=status.HTTP_201_CREATED)
    
class NoticeMailView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = NoticeMailSerialzier

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        in_body = serializer.validated_data.get('body')
        subject = serializer.validated_data.get('subject')
        body_subject = serializer.validated_data.get('body_subject')
        sub_users = User.objects.filter(subscription=True).values('email')
        sub_unknowns = Subsription.objects.values('sub_email')

        send_list = [sub_user['email'] for sub_user in sub_users] + [sub_unknown['sub_email'] for sub_unknown in sub_unknowns]
        send_list = list(dict.fromkeys(send_list))
        #send_list = ['osodofficial@gmail.com']
        context = {
            'body_subject': body_subject,
            'in_body': mark_safe(in_body)
        }
        message = render_to_string('notice.html', context)
        subject = f"[OSOD] {subject}"

        email = EmailMessage(
                subject = subject,
                body = message,
                from_email = 'OSOD <officialosod@gmail.com>',
                bcc = send_list,
                reply_to=['OSOD <officialosod@gmail.com>'],
            )
        email.content_subtype = 'html'
        email.send()
        return Response(status=status.HTTP_201_CREATED)