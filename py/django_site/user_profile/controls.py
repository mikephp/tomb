#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from .models import Profile
from django_site.util import *


def save_profile(backend, user, response=None, *args, **kwargs):
    profile = get_or_none(Profile, user_id=user.id)
    if profile is not None:
        return
    profile = Profile(user_id=user.id)
    profile.provider = backend.name
    profile.nick = user.username
    profile.bio = "(empty)"
    profile.save()
