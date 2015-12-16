#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

def get_or_none(cls, **kwargs):
    try:
        return cls.objects.get(**kwargs)
    except cls.DoesNotExist:
        return None

def assure_user_active(user):
    return user.is_authenticated() and user.is_active

import hashlib
def verification_cookie_of_user(user):
    m = hashlib.sha256()
    m.update(str(user.id))
    m.update(user.username)
    m.update(user.email)
    m.update(str(user.date_joined))
    return m.hexdigest()
