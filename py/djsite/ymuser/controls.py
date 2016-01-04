#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import hashlib
from oauth2client import client, crypt
import traceback
import logging
from ymuser.models import KeyPair, YMUser
from social.apps.django_app.default.models import UserSocialAuth
# from social_auth.db.django_models import UserSocialAuth
from django.conf import settings
# from django.contrib.auth.models import User
import facebook

logger = logging.getLogger(__name__)


def signature(js, private):
    keys = js.keys()
    keys.sort()
    s = ''
    for k in keys:
        if k in ('pub', 'sign'):
            continue
        s += str(js[k])
    s += private
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()

GOOGLE_ACCEPT_CLIENT_IDS = (settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                            '1024550827919-n8bl5dfps3ev40kn327lhh1mb6bof53p.apps.googleusercontent.com',
                            '1024550827919-mnc5opl8h5tn4aq89kcvdohupdc19so7.apps.googleusercontent.com',
                            '1024550827919-a73g29gv3f1smo56mr73nl6l7trg23ap.apps.googleusercontent.com',
                            '1024550827919-kunogrpee6qf7952ir06cbmlh4rhnrku.apps.googleusercontent.com',)


def request_google_auth_service(client_id, token):
    idinfo = client.verify_id_token(token, client_id)
    if idinfo['aud'] not in GOOGLE_ACCEPT_CLIENT_IDS:
        raise crypt.AppIdentityError("Unrecognized client.")
    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise crypt.AppIdentityError("Wrong issuer.")
    idinfo['uid'] = idinfo['sub']
    for (x, y) in (('name', 'username'), ('given_name', 'first_name'), ('family_name', 'last_name')):
        idinfo[y] = idinfo[x] if x in idinfo else ''
    idinfo['provider'] = 'google-oauth2'
    # logger.debug('idinfo = {}'.format(idinfo))
    return idinfo


def request_facebook_auth_service(token):
    g = facebook.GraphAPI(access_token=token)
    data = g.get_object(id='me', fields=[
                        'id', 'email', 'picture', 'name', 'locale', 'first_name', 'last_name'])
    data['username'] = data['name']
    data['picture'] = data['picture']['data']['url']
    data['provider'] = 'facebook'
    data['uid'] = data['id']
    return data


def request_auth_service(provider, client_id, token):
    if provider == 'google':
        auth_data = request_google_auth_service(client_id, token)
        return auth_data
    elif provider == 'facebook':
        auth_data = request_facebook_auth_service(token)
        return auth_data
    raise Exception('Unknown provider: %s' % (provider))

KEY_PAIRS = (('99754106633f94d350db34d548d6091a',  # echo -n "fuck" | md5
              '639bae9ac6b3e1a84cebb7b403297b79'),  # echo -n "you" | md5
             )


def get_private(pub):
    # kp = KeyPair.objects.get(public = pub)
    # pri = kp.private
    # return pri
    for (x, y) in KEY_PAIRS:
        if x == pub:
            return y
    raise Exception('Unknown pubkey: %s' % (pub))


def get_user_id(auth_data):
    provider = auth_data['provider']
    uid = auth_data['uid']
    logger.debug('uid = {}'.format(uid))
    user_social_auth = UserSocialAuth.get_social_auth(provider, uid)
    if user_social_auth:
        user = YMUser.objects.get(id=user_social_auth.user_id)
    else:
        user = YMUser()
    if 'email' in auth_data:
        user.email = auth_data['email']
    if 'username' in auth_data:
        user.username = auth_data['username']
    if 'first_name' in auth_data:
        user.first_name = auth_data['first_name']
    if 'last_name' in auth_data:
        user.last_name = auth_data['last_name']
    if 'picture' in auth_data:
        user.icon_url = auth_data['picture']
    if 'locale' in auth_data:
        user.locale = auth_data['locale']
    # logger.debug('user save called...')
    user.save()
    if user_social_auth:
        return user.id
    user_social_auth = UserSocialAuth(user_id=user.id, provider=provider,
                                      uid=uid, extra_data=auth_data)
    user_social_auth.save()
    return user.id


def verify_client_auth(js):
    pub = js['pub']
    pri = get_private(pub)
    sign = signature(js, pri)
    if sign != js['sign']:
        return False
    return True


def get_user_info(uid):
    user = YMUser.objects.get(id=uid)
    info = {'timeline': user.timeline,
            'premium-to': user.premium_to}
    return info


def set_user_info(uid, js):
    user = YMUser.objects.get(id=uid)
    if 'timeline' in js:
        user.timeline = js['timeline']
    if 'premium-to' in js:
        user.premium_to = js['premium-to']
    user.save()
