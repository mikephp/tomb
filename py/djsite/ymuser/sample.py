#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import hashlib
import requests
import json

def signature(js, private):
    keys = js.keys()
    keys.sort()
    s = ''
    for k in keys:
        if k in ('pub', 'sign'): continue
        s += str(js[k])
    s += private
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()

GOOGLE_TOKEN = """eyJhbGciOiJSUzI1NiIsImtpZCI6Ijc4YjAyNDdlZjVmZDI3YjNjZTcyNzNiNWE0MDRjNGU4NmE5MmEyNGQifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhdF9oYXNoIjoiSExVMWF2SUsxeFdhYnF0WVo0a3FqZyIsImF1ZCI6IjUyNTMxNjc0MjA2Ny1hamlvZWszbDc2NWpiaTBkamdqbmt0ZjhjYWM1YXU4YS5hcHBzLmdvb2dsZXVzZXJjb250ZW50LmNvbSIsInN1YiI6IjEwNDY3Njg3MzI2MjcyNTEwMTk3MSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhenAiOiI1MjUzMTY3NDIwNjctYWppb2VrM2w3NjVqYmkwZGpnam5rdGY4Y2FjNWF1OGEuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJlbWFpbCI6ImRpcnR5c2FsdDE5ODdAZ21haWwuY29tIiwiaWF0IjoxNDQ5NDcyMDE2LCJleHAiOjE0NDk0NzU2MTZ9.CuznsgAyQ-7M2gAgJcrvd8tYgZ63yF3pvOUE2BLImtoV2cfdI9jY4sK5iHSn_K5roZ6k6vMPcqgp4gikbyrbzoCXBs6Bcgju-bAqS6HG1cCfp7WkUUb-3ANNU0Y3Y1QBJVfDcdRAl26agwX_2lrki7hMQMOqobe7ytXY214o6egZ5PXkepcnSBZR30MwgQ2nN51hM8GZ7wENQ73Mjii0DpR-YXKVXkHiqibP95mXwHmH7s9XcaVXxzREKwe4Qu84NmhWY90Y9L7LgUkxprDJ5h_F-B1tFPgGP7V7pm5k2F8R6kyuMjh9OUk3OoO36GnEOACiRHfIrA1unnl39iR5Qg"""

URL = 'http://localhost:8001/ymuser/'
PUB = 'abc'
PRI = 'xyz'
CLIENT_ID = '525316742067-ajioek3l765jbi0djgjnktf8cac5au8a.apps.googleusercontent.com'

def test_token_signin():
    url = URL + 'token-signin/'
    payload = {'token': GOOGLE_TOKEN,
               'client_id': CLIENT_ID,
               'pub': PUB,
               'provider': 'google'}
    sign = signature(payload, PRI)
    payload['sign'] = sign
    r = requests.post(url, data = json.dumps(payload))
    print r.text

def test_user_info():
    url = URL + 'set-user-info/'
    payload = {'pub': PUB, 'uid': 1, 'timeline': 20, 'premium-to' : '2025-10-10'}
    sign = signature(payload, PRI)
    payload['sign'] = sign
    r = requests.post(url, data = json.dumps(payload))
    print r.text

    url = URL + 'user-info/'
    payload = {'pub': PUB, 'uid': 1}
    sign = signature(payload, PRI)
    payload['sign'] = sign
    r = requests.post(url, data = json.dumps(payload))
    print r.text

if __name__ == '__main__':
    test_token_signin()
    test_user_info()
