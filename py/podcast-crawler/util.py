#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from config import *

from pymongo import MongoClient
import pymongo
import requests
from pymongo import InsertOne, DeleteOne, ReplaceOne
import hashlib
import json as json_lib
import redis
from elasticsearch import Elasticsearch
import mmh3
import datetime as dt
import time
import os


class Document(object):

    """Mongo Document"""

    @classmethod
    def from_json(cls, js):
        x = cls()
        x.__dict__ = js
        return x

    def to_json(self):
        return self.__dict__

Client = MongoClient(MONGO_URL)
DB = Client.pdcast
TCache = DB['cache']
# itunes playlist
TPlaylist = DB['playlist']
TPodcast = DB['feed']
TTopList = DB['toplist']

RedisClient = redis.StrictRedis(host=REDIS_URL[0],
                                port=REDIS_URL[1],
                                db=REDIS_URL[2])

# requests settings.
from requests.adapters import HTTPAdapter
Session = requests.Session()
Session.mount('http://', HTTPAdapter(max_retries=MAX_RETRY_NUMBER))
Session.mount('https://', HTTPAdapter(max_retries=MAX_RETRY_NUMBER))


ES = Elasticsearch()

TESBook = DB['esbook']


def create_mongo_index():
    TCache.create_index('key')
    TCache.create_index('tag')

    TPlaylist.create_index('pid')
    TPlaylist.create_index('country')
    TPlaylist.create_index('genres')

    TPodcast.create_index('key')
    TPodcast.create_index('itunes_id')
    TPodcast.create_index('country')
    TPodcast.create_index('genres')
    TPodcast.create_index('language')

    TTopList.create_index('key')
    TESBook.create_index('key')
create_mongo_index()

with open('genres.json') as fh:
    GENRES_MAPPING = json_lib.load(fh)
with open('genres_all.json') as fh:
    GENRES_ALL_MAPPING = json_lib.load(fh)


def get_feed_key(feedUrl):
    return hashlib.sha1(feedUrl).hexdigest()


def fetch_from_network(url, cache_key, tag, now, expireDays, force, cont, *args):
    cr = TCache.find_one({'key': cache_key})
    if 'FORCE_PARSE' in os.environ and cr and 'value' in cr:
        cont(cr['value'], *args)
        return

    offset = expireDays - hash(cache_key) % expireDays
    if not force and cr and cr['updateDate'] > (now - dt.timedelta(days=offset)):
        # print('FETCH FROM NETWORK CACHED. ON DATE %s' % (cache_key))
        return

    print('FETCH FROM NETWORK. %s' % (cache_key))
    if not cr:
        cr = {'key': cache_key,
              'tag': tag,
              'sign': 0,
              'headers': {}}
    headers = cr.get('headers', {})
    res = requests.get(url, timeout=10, headers=headers)

    # NOT MODIFIED.
    if res.status_code == 304:
        print('FETCH FROM NETWORK CACHED. NOT MODIFIED %s' % (cache_key))
        cr['updateDate'] = now
        TCache.replace_one({'key': cache_key}, cr)
        return

    # FETCH FAILED.
    if res.status_code != 200:
        print('FETCH FROM NETWORK FAILED. url = %s code = %d' %
              (url, res.status_code))
        # cr['updateDate'] = now
        TCache.replace_one({'key': cache_key}, cr)
        return

    value = res.content
    if 'Last-Modified' in res.headers:
        headers['If-Modified-Since'] = res.headers['Last-Modified']
    if 'ETag' in res.headers:
        headers['If-None-Match'] = res.headers['ETag']
    cr['headers'] = headers

    sign = mmh3.hash(value)
    if cr.get('sign', 0) == sign:
        print('FETCH FROM NETWORK CACHED. ON SIGN %s' % (cache_key))
        cr['updateDate'] = now
        TCache.replace_one({'key': cache_key}, cr)
        return

    cr['sign'] = sign
    cr['value'] = value
    cr['updateDate'] = now
    cont(cr['value'], *args)
    TCache.replace_one({'key': cache_key}, cr, upsert=True)
