#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import web
import json
from oauth2client import client, crypt
import facebook

urls = ("/tokensignin", 'TokenSignIn',
        '/tokensignin-fb', 'TokenSignInFB',)

app = web.application(urls, globals())

"""
{u'picture': u'https://lh6.googleusercontent.com/-oVnyjJBb5w4/AAAAAAAAAAI/AAAAAAAAAZ8/DDHwU4jKgBI/s96-c/photo.jpg', u'aud': u'525316742067-ajioek3l765jbi0djgjnktf8cac5au8a.apps.googleusercontent.com', u'family_name': u'yan', u'iss': u'https://accounts.google.com', u'email_verified': True, u'name': u'zhang yan', u'at_hash': u'F4mfL38K7jnT7kcZc68vUA', u'given_name': u'zhang', u'exp': 1449466730, u'azp': u'525316742067-ajioek3l765jbi0djgjnktf8cac5au8a.apps.googleusercontent.com', u'iat': 1449463130, u'locale': u'zh-CN', u'email': u'dirtysalt1987@gmail.com', u'sub': u'104676873262725101971'}
"""
class TokenSignIn:
    def POST(self):
        data = web.data()
        js = json.loads(data)
        token = js['idtoken']
        print('token = %s' % token)
        try:
            # CLIENT_ID = '525316742067-ajioek3l765jbi0djgjnktf8cac5au8a.apps.googleusercontent.com'
            CLIENT_ID = '1024550827919-a73g29gv3f1smo56mr73nl6l7trg23ap.apps.googleusercontent.com'
            idinfo = client.verify_id_token(token, CLIENT_ID)
            # If multiple clients access the backend server:
            # if idinfo['aud'] not in [ANDROID_CLIENT_ID, IOS_CLIENT_ID, WEB_CLIENT_ID]:
            #     raise crypt.AppIdentityError("Unrecognized client.")
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise crypt.AppIdentityError("Wrong issuer.")
            # if idinfo['hd'] != APPS_DOMAIN_NAME:
            #     raise crypt.AppIdentityError("Wrong hosted domain.")
        except crypt.AppIdentityError as e:
            # Invalid token
            print e
            return 'NOT OK'
        print idinfo
        userid = idinfo['sub']
        return 'OK'

"""
In [19]: g.get_object(id='me', fields=['email', 'picture','birthday','name','locale'])
Out[19]:
{'email': 'dirtysalt1987@gmail.com',
 'id': '983661618394966',
 'locale': 'zh_CN',
 'name': u'\u7ae0\u708e',
 'picture': {'data': {'is_silhouette': False,
   'url': 'https://scontent.xx.fbcdn.net/hprofile-ash2/v/t1.0-1/c95.25.310.310/s50x50/246901_101089229985547_3411537_n.jpg?oh=1277182b9802b75c4fcfee570bc8adcc&oe=5713645F'}}}
"""
class TokenSignInFB:
    def GET(self):
        data = web.input(token = '')
        token = data.token
        return self.handle(token)

    def POST(self):
        data = web.data()
        js = json.loads(data)
        token = js['idtoken']
        return self.handle(token)

    def handle(self, token):
        print('token = %s' % token)
        try:
            g = facebook.GraphAPI(access_token = token)
            data = g.get_object(id='me', fields = ['email', 'picture', 'name', 'locale'])
        except Exception as e:
            print e
            return 'NOT OK'
        print data
        return 'OK'

if __name__ == '__main__':
    app.run()
