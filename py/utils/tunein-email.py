#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import pymongo
import snappy
import requests
from bs4 import BeautifulSoup
import hashlib
import bson
import json
import time

client = pymongo.MongoClient()
cache_table = client.test.cache_table

urls = """USA http://tunein.com/radio/United-States-r100436/
Canada http://tunein.com/radio/Canada-r101227/
Australia http://tunein.com/radio/Australia-r101356/""".split('\n')

urls = map(lambda x: map(lambda y: y.strip(), x.split()), urls)

class SessionThrottle(object):
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit
        self.rate_cnt = 0
        self.rate_ts = time.time()

    def set_rate_limit(self, v):
        self.rate_limit = v

    def run(self):
        if self.rate_limit:
            now_ts = time.time()
            ts = self.rate_cnt / self.rate_limit
            self.rate_cnt += 1
            delay = ts - (now_ts - self.rate_ts)
            if delay > 0.1:
                time.sleep(delay)
                return delay
        return 0

throttle = SessionThrottle(2)

def get_sha1_key(s):
    return hashlib.sha1(s).hexdigest()

def _get(key, callback, args):
    r = cache_table.find_one({'_id': key})
    if not r:
        content = callback(*args)
        data = bson.binary.Binary(snappy.compress(content))
        cache_table.insert_one({'_id': key, 'data': data})
    else:
        data = r['data']
    content = snappy.decompress(data)
    return content

def request_url_callback(url):
    throttle.run()
    r = requests.get(url)
    return r.content

def parse_url_callback(url, selector):
    content = _get(get_sha1_key(url), request_url_callback, (url, ))
    bs = BeautifulSoup(content)
    xs = map(lambda x: x.attrs['href'], bs.select(selector))
    content = json.dumps(xs)
    return content

def get_states(url):
    key = get_sha1_key('tunein-state-' + url)
    content = _get(key, parse_url_callback, (url, '#mainContent > div > div.group.clearfix.linkmatrix > ul > li > a'))
    xs = json.loads(content)
    links = map(lambda x: 'http://tunein.com' + x, xs)
    return links

def get_stations(url):
    key = get_sha1_key('tunein-station-' + url)
    content = _get(key, parse_url_callback, (url, '#mainContent > div > div > ul > li > a'))
    xs = json.loads(content)
    links = map(lambda x: 'http://tunein.com' + x, xs)
    return links

import re
EMAIL_REGEX = re.compile(r'mailto:([^"]+)')
def get_email(url):
    ct = _get(get_sha1_key(url), request_url_callback, (url, ))
    m = EMAIL_REGEX.search(ct)
    if m: return m.groups()[0]
    return None

import json
import os

def main():
    d = {}
    cid = -1
    call = len(urls)
    for (country, url) in urls:
        cid += 1
        emails = set()
        states = get_states(url)
        print('extending states ...')
        # what if we have more than two level states.
        states2 = []
        states2.extend(states)
        for s in states:
            states2.extend(get_states(s))
        states = list(set(states2))
        print('country = %s[%d/%d], states = %d' % (country, cid, call, len(states)))
        rall = len(states)
        for (rid, state) in enumerate(states):
            stations = get_stations(state)
            print('country = %s[%d/%d], state = %s[%d/%d], stations = %d' % (
                country, cid, call, state, rid, rall, len(stations)))
            for st in stations:
                email = get_email(st)
                if not email: continue
                emails.add(email)
        d[country] = list(emails)
        print('country = %s, emails = %d' % (country, len(emails)))

    with open('tunein-email.txt', 'w') as fh:
        for key in d:
            emails = d[key]
            lines = list(emails)
            lines.insert(0, '>>>>> country (%s) <<<<<' % key)
            fh.writelines(map(lambda x: x + '\n', lines))

if __name__ == '__main__':
    main()
