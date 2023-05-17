from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class User(AbstractUser):
    email = models.EmailField(max_length=50,unique=True)
    password = models.CharField(max_length=512)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    username = None
    nickname = models.CharField(max_length=50, unique=True, null=True)
    name = models.CharField(max_length=50, null=True)
    subscription = models.BooleanField(default=False, null=True)
    liked_num = models.IntegerField(default=0, null=True)
    is_first = models.BooleanField(default=True, null=True)

class Feedback(models.Model):
     body = models.CharField(max_length=200)
     