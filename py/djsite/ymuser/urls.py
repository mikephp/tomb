#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('ymuser',
    url(r'token-signin/', views.token_signin),
    url(r'get-user-info/', views.get_user_info),
    url(r'set-user-info/', views.set_user_info),
)
