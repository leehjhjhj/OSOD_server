from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(max_length=50,unique=True)
    password = models.CharField(max_length=512)
    username = models.CharField(max_length=10,unique=True, null=True)
