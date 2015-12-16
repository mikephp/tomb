#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate as auth_authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import django_rq
import uuid
from social.apps.django_app.default.models import UserSocialAuth
from .util import *
from django.template import RequestContext
from django.template.context_processors import csrf
from user_profile.models import Profile
from user_profile.controls import save_profile
from django.contrib.auth.decorators import user_passes_test

# Create your views here.

def throw404(request):
    raise Http404()
def throw500(request):
    x = c

# @login_required(login_url='/login')
@user_passes_test(assure_user_active, login_url='/login')
def home(request):
    ctx = {'request': request}
    user = request.user
    profile = get_or_none(Profile, user_id = user.id)
    ctx['user'] = user
    ctx['provider'] = 'insite'
    ctx['auth_data'] = ''
    if profile:
        ctx['provider'] = profile.provider
        if profile.provider in ('facebook', 'google-oauth2',):
            auth = UserSocialAuth.objects.get(provider = profile.provider, user_id = user.id)
            ctx['auth_data'] = auth.extra_data
    return render_to_response('djsite/home.html', ctx)

def login(request):
    if request.method == 'GET':
        next_url = request.GET.get('next', '/home')
        c = {'next': next_url}
        c.update(csrf(request))
        return render_to_response('djsite/login.html', c)
    else: # POST
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', '/home')
        user = auth_authenticate(username = username, password = password)
        # if user and user.is_active:
        if user and user.is_active:
            auth_login(request, user)
            return redirect(next_url)
        elif user and not user.is_active:
            ctx = {}
            ctx['username'] = username
            ctx['email'] = user.email
            ctx['cookie'] = verification_cookie_of_user(user)
            return HttpResponse('<a href="/active?username=%s&email=%s&cookie=%s">Active link</a>' % (
                username, email, cookie))
        else:
            c = {'next': next_url, 'auth_fail' : True,
                 'username': username, 'password': password}
            c.update(csrf(request))
            return render_to_response('djsite/login.html', c)

def active(request):
    username = request.GET.get('username', '')
    cookie = request.GET.get('cookie', '')
    user = get_or_none(User, username = username)
    if not user: return HttpResponse('user = %s not found' % username)
    cookie_exp = verification_cookie_of_user(user)
    if cookie_exp != cookie: return HttpResponse('invalid link')
    # save to user profile.
    save_profile('insite', user)
    # set user active.
    user.is_active = True
    user.save()
    return HttpResponse('active OK. go to <a href="/home">home</a>')

def register(request):
    ctx = {}
    ctx.update(csrf(request))
    if request.method == "GET":
        return render_to_response('djsite/register.html', ctx)
    elif request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        user = get_or_none(User, username = username)
        # 用户已经存在.
        if user is not None:
            ctx['error'] = 'user %s already registered' % (username)
            return render_to_response('djsite/register.html', ctx)
        # 创建账号，但是不激活. 默认密码xxx
        user = User.objects.create_user(username = username,
                                        email = email,
                                        password = 'xxx')
        user.is_active = False
        user.save()
        # don't save to user profile.
        cookie = verification_cookie_of_user(user)
        return HttpResponse('Register OK. <a href="/active?username=%s&email=%s&cookie=%s">Active link</a>' % (
            username, email, cookie))

def logout(request):
    auth_logout(request)
    return redirect('/home')

def dump(request):
    # django_rq.enqueue()
    user = request.user
    ctx = {'path': request.path,
           'full_path': request.get_full_path(),
           'user': user,
           'body': request.body,
           'cookie': request.COOKIES,
           'GET': request.GET,
           'POST': request.POST,
           'session':request.session.items(),
           'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown'),
    }
    return render_to_response('djsite/dump.html', ctx)
