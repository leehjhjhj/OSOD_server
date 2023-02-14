from django.db import models
from accounts.models import User

class Sentence(models.Model):
    sentence = models.CharField(max_length=200)
    discription = models.CharField(max_length=200)
    created_at = models.DateTimeField(null=True)
    is_valid = models.BooleanField(default=False, null=True)
    translate = models.CharField(max_length=200, null=True)


class Post(models.Model):
    body = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, null=True)
    like_users = models.ManyToManyField(User, related_name='like', null=True)
    like_num = models.IntegerField(null=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

class Subsription(models.Model):
    sub_email = models.EmailField(unique=True, max_length=50)
    sub_nickname = models.CharField(max_length=50, unique=True, null=True)