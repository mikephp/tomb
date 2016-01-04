#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import hashlib
import requests
import json


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

# URL = 'http://localhost:8001/ymuser/'
URL = 'https://api.yogamonkey.fit/ymuser/'
PUB = '99754106633f94d350db34d548d6091a'
PRI = '639bae9ac6b3e1a84cebb7b403297b79'

CLIENT_ID = '962722732387-okdgpbfgsn283j59r4sc0ea9q782j2ir.apps.googleusercontent.com'

GOOGLE_TOKEN = 'ya29.XwI6Uem88dP7BJlN8GTSXzTYK9FnxTVVmNZjVUyLd6C34Yn-NRhTqnqvVA-Il8bEpnB0'


def test_token_signin():
    url = URL + 'token-signin/'
    payload = {'token': GOOGLE_TOKEN,
               'client_id': CLIENT_ID,
               'pub': PUB,
               'provider': 'google'}
    sign = signature(payload, PRI)
    payload['sign'] = sign
    r = requests.post(url, data=json.dumps(payload))
    print r.text

FB_TOKEN = 'CAACEdEose0cBAII1uUzc1xZCFMfQjgviupk9z4Fdg1qNLRB6kxYsPL6ZCQbtkZAd6dAJhsd69pr487Mrcp86lsJfFXJjzTwhQYapHlJxKgkJPYmGpMHUBfCZCK0XjLiUUEXK2qZAEmYIWjZBbWBDkcYPZB216ravO0ncbJmwSZCHKoDbkEu63lYGUTbK9fsZAMUGlilp0uY5IhgZDZD'


def test_token_signin2():
    url = URL + 'token-signin/'
    payload = {'token': FB_TOKEN,
               'client_id': '',
               'pub': PUB,
               'provider': 'facebook'}
    sign = signature(payload, PRI)
    payload['sign'] = sign
    r = requests.post(url, data=json.dumps(payload))
    print r.text


def test_user_info():
    url = URL + 'set-user-info/'
    payload = {'pub': PUB, 'uid': 1,
               'timeline': 20, 'premium-to': '2025-10-10'}
    sign = signature(payload, PRI)
    payload['sign'] = sign
    r = requests.post(url, data=json.dumps(payload))
    print r.text

    url = URL + 'get-user-info/'
    payload = {'pub': PUB, 'uid': 1}
    sign = signature(payload, PRI)
    payload['sign'] = sign
    r = requests.post(url, data=json.dumps(payload))
    print r.text

if __name__ == '__main__':
    test_token_signin()
    # test_user_info()
    test_token_signin2()
