from django.conf import settings
from django.db import models

# Create your models here.

class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    provider = models.CharField(max_length=32, default = 'insite', null = False)
    nick = models.CharField(max_length=100)
    bio = models.CharField(max_length=100)
