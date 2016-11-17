#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import requests
import urlparse
import os
import json
import traceback
import time

class FirebaseRealtimeDB():
    ROOT_URL = '' #no trailing slash

    def __init__(self, root_url, auth_token=None, ss = None):
        self.ROOT_URL = root_url.rstrip('/')
        self.auth_token = auth_token
        self.ss = ss or requests.session()

    #These methods are intended to mimic Firebase API calls.

    def child(self, path):
        root_url = '%s/' % self.ROOT_URL
        url = urlparse.urljoin(root_url, path.lstrip('/'))
        return FirebaseRealtimeDB(url, self.auth_token, self.ss)

    def parent(self):
        url = os.path.dirname(self.ROOT_URL)
        #If url is the root of your Firebase, return None
        up = urlparse.urlparse(url)
        if up.path == '':
            return None #maybe throw exception here?
        return FirebaseRealtimeDB(url, self.auth_token, self.ss)

    def name(self):
        return os.path.basename(self.ROOT_URL)

    def toString(self):
        return self.__str__()
    def __str__(self):
        return self.ROOT_URL

    def set(self, value):
        return self.put(value)

    def push(self, data):
        return self.post(data)

    def update(self, data):
        return self.patch(data)

    def remove(self):
        return self.delete()


    #These mirror REST API functionality

    def put(self, data):
        return self.__request('put', data = data)

    def patch(self, data):
        return self.__request('patch', data = data)

    def get(self):
        return self.__request('get')

    #POST differs from PUT in that it is equivalent to doing a 'push()' in
    #Firebase where a new child location with unique name is generated and
    #returned
    def post(self, data):
        return self.__request('post', data = data)

    def delete(self):
        return self.__request('delete')


    #Private

    def __request(self, method, **kwargs):
        #Firebase API does not accept form-encoded PUT/POST data. It needs to
        #be JSON encoded.
        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])

        params = {}
        if self.auth_token:
            if 'params' in kwargs:
                params = kwargs['params']
                del kwargs['params']
            params.update({'auth': self.auth_token})

        r = self.ss.request(method, self.__url(), params=params, **kwargs)
        r.raise_for_status() #throw exception if error
        return r.json()


    def __url(self):
        #We append .json to end of ROOT_URL for REST API.
        return '%s.json' % self.ROOT_URL

class FirebaseCloudMessaging():

    def __init__(self, auth_token, ss = None):
        self.auth_token = auth_token
        self.ss = ss or requests.session()
        self.fcm_url = 'https://fcm.googleapis.com/fcm/send'

    # https://firebase.google.com/docs/cloud-messaging/topic-messaging#http_post_request
    def _send(self, post_data, retry = 3):
        delay = 2
        headers = {
            'Content-Type':'application/json',
            'Authorization': 'key=%s' % (self.auth_token)
        }
        while retry:
            failed = False
            try:
                res = self.ss.post(self.fcm_url, data = json.dumps(post_data),
                                   headers = headers)
                if res.status_code != 200:
                    # print('+++ ! 200. %s' % res.content.strip())
                    failed = True
                else:
                    # print res.content.strip()
                    pass
            except:
                traceback.print_exc()
                failed = True

            if failed:
                retry -= 1
                time.sleep(delay)
                delay *= 1.5
                continue
            else:
                break
        return retry > 0

    def send_data(self, post_data, tokens = None, time_to_live = 3600 * 24 * 2):
        MAX_REGISTRATION_NUMBER = 500
        if time_to_live:
            post_data['time_to_live'] = time_to_live
        post_data['priority'] = 'high'

        if 'to' not in post_data:
            offset = 0
            while offset < len(tokens):
                reg_ids = tokens[offset: offset + MAX_REGISTRATION_NUMBER]
                post_data['registration_ids'] = reg_ids
                if self._send(post_data):
                    print('!!!!! OK')
                else:
                    print('~~~~~ Failed')
                offset += MAX_REGISTRATION_NUMBER
        else:
            if self._send(post_data):
                print('!!!!! OK')
            else:
                print('~~~~~ Failed')

    # note(yan): 通过fcm向iOS发送消息的话，priority一定要设置为high, notification.body字段是必需的。不要设置time_to_live.
    # http://stackoverflow.com/questions/37332415/cant-send-push-notifications-using-the-server-api/37550067#37550067

    def send_notification(self, body, to):
        post_data = {'notification': {'body': body}, 'to': to}
        self.send_data(self, post_data)
