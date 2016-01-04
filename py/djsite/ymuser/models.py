from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class KeyPair(models.Model):
    public = models.CharField(max_length = 255, unique = True)
    private = models.CharField(max_length = 255)
    description = models.CharField(max_length = 255)

class YMUser(AbstractUser):
    timeline = models.PositiveIntegerField(default = 0)
    premium_to = models.DateField(auto_now_add = True)
    locale = models.CharField(max_length = 32, default = 'en')
    icon_url = models.URLField(max_length = 1024)
