from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class KeyPair(models.Model):
    public = models.CharField(max_length = 1024, unique = True)
    private = models.CharField(max_length = 1024)
    description = models.CharField(max_length = 256)

class YMUser(AbstractUser):
    timeline = models.PositiveIntegerField(default = 0)
    premium_to = models.DateField(auto_now_add = True)
