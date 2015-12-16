#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns('bookstore',
   url(r'index/', views.index),
   url(r'contact/', views.contact),
   url(r'thanks/', views.thanks),
)
