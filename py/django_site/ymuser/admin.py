from django.contrib import admin
from .models import *

# Register your models here.

class KeyPairAdmin(admin.ModelAdmin):
    list_display = ('id', 'public', 'description')

class YMUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'timeline', 'premium_to')

admin.site.register(KeyPair, KeyPairAdmin)
admin.site.register(YMUser, YMUserAdmin)
