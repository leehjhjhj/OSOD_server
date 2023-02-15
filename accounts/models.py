from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class User(AbstractUser):
    email = models.EmailField(max_length=50,unique=True)
    password = models.CharField(max_length=512)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    username = None
    nickname = models.CharField(max_length=50, unique=True, null=True)
    name = models.CharField(max_length=50, unique=True, null=True)
    subscription = models.BooleanField(default=False, null=True)
    liked_num = models.IntegerField(default=0, null=True)
