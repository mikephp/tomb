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
URL = 'http://api.yogamonkey.fit/ymuser/'
PUB = '99754106633f94d350db34d548d6091a'
PRI = '639bae9ac6b3e1a84cebb7b403297b79'

CLIENT_ID = '1024550827919-a73g29gv3f1smo56mr73nl6l7trg23ap.apps.googleusercontent.com'

GOOGLE_TOKEN = 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImM2ZDBjMWFjYzExY2IzMDg4MDQyMzg3YWMyYzE5NjA0NDAyOWViNzQifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhdF9oYXNoIjoiNDM4X3Y2RzFkOTVkNFZTQ1oxeUhrUSIsImF1ZCI6IjEwMjQ1NTA4Mjc5MTktYTczZzI5Z3YzZjFzbW81Nm1yNzNubDZsN3RyZzIzYXAuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDQ2NzY4NzMyNjI3MjUxMDE5NzEiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXpwIjoiMTAyNDU1MDgyNzkxOS1hNzNnMjlndjNmMXNtbzU2bXI3M25sNmw3dHJnMjNhcC5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsImVtYWlsIjoiZGlydHlzYWx0MTk4N0BnbWFpbC5jb20iLCJpYXQiOjE0NTE4ODM2MTEsImV4cCI6MTQ1MTg4NzIxMSwibmFtZSI6InpoYW5nIHlhbiIsInBpY3R1cmUiOiJodHRwczovL2xoNi5nb29nbGV1c2VyY29udGVudC5jb20vLW9WbnlqSkJiNXc0L0FBQUFBQUFBQUFJL0FBQUFBQUFBQVo4L0RESHdVNGpLZ0JJL3M5Ni1jL3Bob3RvLmpwZyIsImdpdmVuX25hbWUiOiJ6aGFuZyIsImZhbWlseV9uYW1lIjoieWFuIiwibG9jYWxlIjoiemgtQ04ifQ.ZxGx6x1rljv7QS36lf1UA1pINgdxw3LJog6Bmq8l1IRB9Yww3YSQdGl_53PcGOpHeCgpQDWNnHERhrYD8Ei-I8PNN2kj8mx3ZfE16XZsX7f4jbtLAfw3i6t23Cu4fso5Ktz1gjOt7nIOIoNPC286TpBEvRrFcqIrxj3Cf-57ooaEGHl5k3r1U08xIkPv4Ikr7yRhUjjU2SpB3nSjX66CqVKYmD9OtHsRDxZJpXTps0jfzNBdNVzPqIqrFndDVbqWad9T-p8A-t5M_yloRdEZEn0Fd8grHYID_ooQODBDNMYqROi0LuepRRFgX5XyzYXLDrtLnQegA3qFB3GEqu596w'


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

FB_TOKEN = 'CAAYmGJhWxrkBAOI3awmefXZCxUdHJmxj09jKMzQVowPm2TI5KYxEsJOmH0UuK0oNXWRQVOKLzFDwaMEnyBPGqQjafRmVLi6Hr5JSfRLrHqMrUdk0VijMFI8ZBSTqSLy7WlYlpBWjBgawzzqEYNhjbogQMSNuZBsHwZCU8nzGSmRTKOgWnC9c0NzK254GleYZC06deGSKT7pMcWw7NHORUmzfZALWYKc9YZD'


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
