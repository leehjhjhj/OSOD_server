from django.test import TestCase
from django.utils.timezone import datetime
from server.writing.models import *

now = datetime.now()
target_post = Post.objects.get(pk=70)
cal_time = now - target_post.created_at
print(cal_time)
