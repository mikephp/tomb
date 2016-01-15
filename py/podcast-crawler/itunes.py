#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from gevent import monkey
monkey.patch_all()

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from config import *

from pymongo import MongoClient
import pymongo
from pymongo import InsertOne, DeleteOne, ReplaceOne


import gevent
from gevent.pool import Pool
import random
import requests
import os
import urllib2

import datetime as dt
import json as json_lib
import time

from bs4 import BeautifulSoup
import re

# ====================
# migrate db from mysql to mongo
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import *

Engine = create_engine('mysql+mysqldb://%s:%s@%s/%s' %
                       (DB_USER, DB_PASS, DB_HOST, DB_NAME), encoding='utf-8', echo=False, pool_recycle=3600)
Base = declarative_base()
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=Engine)
Client = MongoClient(MONGO_URL)
DB = Client.pdcast
TCache = DB.cache
TPlaylist = DB.playlist


class Podcast(Base):
    __tablename__ = 'itunes'
    # from itunes
    pid = Column(Integer, primary_key=True)
    country = Column(String(16), index=True)
    genre = Column(Integer, index=True)
    __table_args__ = (Index('country_genre', "country", "genre"), )
    title = Column(TEXT)
    authorId = Column(Integer)
    authorName = Column(TEXT)
    feedUrl = Column(TEXT)
    cover30 = Column(TEXT)
    releaseDate = Column(DateTime)
    trackCount = Column(Integer)
    genreText = Column(TEXT)
    skip = Column(Integer)  # should we skip it?
    wellFormed = Column(Integer)  # content of feedUrl is well-formed?
    parsedDate = Column(DateTime)  # when this feedUrl is parsed.
    description = Column(TEXT)
    lang = Column(String(16), index=True)


class Cache(Base):
    __tablename__ = 'cache'
    mykey = Column(String(255), primary_key=True)
    tag = Column(String(16), index=True)
    value = Column(MEDIUMTEXT)
    updateDate = Column(DateTime)


def copy_cache():
    session = Session()
    docs = []
    for cr in session.query(Cache).all():
        r = TCache.find_one({'key': cr.mykey})
        if r:
            continue
        doc = {'key': cr.mykey,
               'tag': cr.tag,
               'value': cr.value,
               'updateDate': cr.updateDate}
        docs.append(doc)
        if len(docs) >= 1000:
            print('insert 1000 docs...')
            TCache.insert_many(docs)
            docs = []
    if len(docs):
        print('insert %d docs...' % (len(docs)))
        TCache.insert_many(docs)
    return
# ====================


class MongoObject(object):

    def __init__(self, js):
        self.__dict__ = js

    @classmethod
    def from_json(cls, js):
        return cls(js)

    def to_json(self):
        return self.__dict__


def create_table():
    TCache.create_index('key')
    TCache.create_index('tag')
    TPlaylist.create_index('pid')
    TPlaylist.create_index('country')
    TPlaylist.create_index('genre')
    TPlaylist.create_index('lang')


def make_combination(shuffle=False):
    comb = []
    for country in ITUNES_COUNTRY_CODE.values():
        if country.find('_') != -1:
            continue
        for genre in ITUNES_PODCAST_GENRE_CODE.values():
            comb.append((country, genre))
    if shuffle:
        random.shuffle(comb)
    else:
        comb.sort(lambda x, y: cmp(x[0], y[0]))
    return comb


def down_index(comb):
    pool = Pool(size=8)
    URL = 'https://itunes.apple.com/%s/genre/id%d?mt=2'
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=INDEX_CACHE_EXPIRE_DAYS)

    for (country, genre) in comb:
        def f(country, genre):
            index_key = 'idx_%s_%d' % (country, genre)
            cr = TCache.find_one({'key': index_key})
            if cr and cr.updateDate > expireDate:
                # print('DOWN INDEX CACHED. (%s, %d)' % (country, genre))
                return

            print('DOWN INDEX. (%s, %d)' % (country, genre))
            url = URL % (country, genre)
            res = requests.get(url)
            if res.status_code != 200:
                print('DOWN INDEX FAILED. url = %s code = %d' %
                      (url, res.status_code))
                return
            value = res.text.encode('utf-8')
            if cr:
                cache = cr
            else:
                cache = {'key': index_key,
                         'tag': 'index'}
            cache['value'] = value
            cache['updateDate'] = now
            TCache.update_one({'key': index_key}, cache, upsert=True)
        g = gevent.spawn(f, country, genre)
        pool.add(g)
    pool.join()
    print('DOWN INDEX DONE')


def parse_index_1(country, genre):
    index_key = 'idx_%s_%d' % (country, genre)
    r = TCache.find_one({'key': index_key})
    if not r:
        print('INDEX NOT EXISTED. (%s, %d)' % (country, genre))
        return
    data = r['value']
    bs = BeautifulSoup(data)
    pds = bs.select('div[id="selectedcontent"] ul li a')
    print('PARSE INDEX (%s, %d)' % (country, genre))
    pids = set()
    for pd in pds:
        title = pd.get_text().encode('utf-8')
        link = pd.attrs['href']
        m = re.search(r'/id(\d+)\?mt=2', link)
        try:
            pid = int(m.groups(1)[0])
        except:
            print('PARSE INDEX FAILED. link = %s' % (link))
            continue
        # print(link, pid)
        if pid in pids:
            continue
        pids.add(pid)
        r = TPlaylist.find_one({'pid': pid})
        if not r:
            r = {'pid': pid,
                 'country': [country],
                 'genres': [genre],
                 'title': title}
        else:
            r.title = title
            if not country in r.country:
                r.country.append(country)
            if not genre in r.genres:
                r.genres.append(genre)
        TPlaylist.update_one({'pid': pid}, r, upsert=True)
    print('PARSE INDEX DONE')


def parse_index(comb):
    for (country, genre) in comb:
        parse_index_1(country, genre)


def down_lookup():
    pids = TPlaylist.find(PIDS_QUERY, projection=('pid',))
    pool = Pool(size=4)
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=LOOKUP_CACHE_EXPIRE_DAYS)

    def f(pid):
        lookup_key = 'lkp_%d' % (pid)
        cr = TCache.find_one({'key': lookup_key})
        if cr and cr.updateDate > expireDate:
            # print('DOWN LOOKUP CACHED. pid = %d' % (pid))
            return
        print('DOWN LOOKUP. pid = %d' % pid)
        url = 'https://itunes.apple.com/lookup?id=%d' % (pid)
        res = requests.get(url)
        if res.status_code != 200:
            print("DOWN LOOKUP FAILED. url = %s code = %d" %
                  (url, res.status_code))
            return
        # print(res.encoding)
        value = res.text.encode('utf-8')
        if cr:
            cache = cr
        else:
            cache = {'key': lookup_key,
                     'tag': 'lookup'}
        cache['value'] = value
        cache['updateDate'] = now
        TCache.update_one({'key': lookup_key}, cache, upsert=True)
        time.sleep(1)

    for pid in pids:
        g = gevent.spawn(f, pid)
        pool.add(g)
    pool.join()
    print('DOWN LOOKUP DONE')


def collect_genres():
    store = {}
    pids = TPlaylist.find(PIDS_QUERY, projection=('pid', ))
    pool = Pool(size=8)

    def f(pid):
        lookup_key = 'lkp_%d' % (pid)
        cr = TCache.find_one({'key': lookup_key})
        if not cr:
            print('LOOKUP NOT EXISTED. pid = %d' % (pid))
            return
        json = json_lib.loads(cr.value)
        if json['resultCount'] != 1:
            if json['resultCount'] != 0:
                print('PARSE LOOKUP FAILED. result count %d. pid = %d' %
                      (json['resultCount'], pid))
            return
        data = json['results'][0]
        genreIds = map(lambda x: int(x), data['genreIds'])
        genres = data['genres']
        for (idx, genreId) in enumerate(genreIds):
            genre = genres[idx]
            store[genre] = genreId

    for pid in pids:
        g = gevent.spawn(f, pid)
        pool.add(g)
    pool.join()
    print(store)
    print('COLLECT GENRES DONE')


def parse_lookup():
    rs = TPlaylist.find(PIDS_QUERY)
    pool = Pool(size=32)

    def f(r):
        pid = r.pid
        lookup_key = 'lkp_%d' % (pid)
        cr = TCache.find_one({'key': lookup_key})
        if not cr:
            print('LOOKUP NOT EXISTED. pid = %d' % (pid))
            return
        print('PARSE LOOKUP. pid = %d' % (pid))
        # validate json data.
        json = json_lib.loads(cr.value)
        if json['resultCount'] != 1:
            if json['resultCount'] != 0:
                print('PARSE LOOKUP FAILED. result count %d. pid = %d' %
                      (json['resultCount'], pid))
            return
        data = json['results'][0]
        # some issues when comparing datetime.
        if not FORCE_PARSE_LOOKUP and \
                r.trackCount == data['trackCount'] and \
                r.feedUrl == data['feedUrl']:
            # print('PARSE LOOKUP CACHED. pid = %d' % (pid))
            return
        genresId = data['genresIds']
        if 'artworkUrl30' in data:
            r.cover30 = data['artworkUrl30']
        if 'releaseDate' in data:
            r.releaseDate = data['releaseDate']
        if 'trackCount' in data:
            r.trackCount = data['trackCount']
        if 'feedUrl' in data:
            r.feedUrl = data['feedUrl']
        if 'artistId' in data:
            r.authorId = data['artistId']
        if 'artistName' in data:
            r.authorName = data['artistName'].encode('utf-8')
        for x in genresId:
            if x in r.genres:
                r.genres.append(x)
        TPlaylist.update_one({'pid': pid}, r)

    for r in rs:
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    print('PARSE LOOKUP DONE')


def down_feed():
    rs = TPlaylist.find(PIDS_QUERY)
    pool = Pool(size=8)
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=FEED_CACHE_EXPIRE_DAYS)

    def f(r):
        if r.skip:
            return
        pid = r.pid
        feed_key = 'feed_%d' % (pid)
        cr = TCache.find_one({'key': feed_key})
        if cr and cr.updateDate > expireDate:
            # print('DOWN FEED CACHED. pid = %d' % pid)
            return
        url = r.feedUrl
        print('DOWN FEED. pid = %d. url = %s' % (pid, url))
        try:
            res = requests.get(url, timeout=10)
        except:
            print('DOWN FEED FAILED. CONNECTION ERROR. pid = %d, url = %s' %
                  (pid, url))
            return
        if res.status_code != 200:
            print('DOWN FEED FAILED. pid = %d, url = %s http-code = %d' %
                  (pid, url, res.status_code))
            if res.status_code in (403, 404):
                r.skip = 1
                TPlaylist.update_one({'pid': pid}, r)
            return
        value = res.text.encode('utf-8')
        if len(value) > (1 << 21):
            r.skip = 1
            TPlaylist.update_one({'pid': pid}, r)
            return
        if cr:
            cache = cr
        else:
            cache = {'key': feed_key,
                     'tag': 'feed'}
        cache['value'] = value
        cache['updateDate'] = now
        TCache.update_one({'key': feed_key}, cache, upsert=True)

    for r in rs:
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    print('DOWN FEED DONE')


import feedparser
import xml.dom.minidom


def extract_detail(r, now, data):
    detail = {'lang': '',
              'desc': ''}
    try:
        dom = xml.dom.minidom.parseString(data)
        d = dom.getElementsByTagName(
            'description') or dom.getElementsByTagName('itunes:summary')
        if d:
            detail['desc'] = d[0].firstChild.data
        d = dom.getElementsByTagName('language')
        if d:
            detail['lang'] = d[0].firstChild.data
    except:
        d = feedparser.parse(data)
        feed = d['feed']
        if 'description' in feed:
            detail['desc'] = feed['description']
        if 'summary' in feed:
            detail['desc'] = feed['summary']
        if 'language' in feed:
            detail['lang'] = feed['language']
    r.description = detail['desc'].encode('utf-8').strip()
    r.lang = detail['lang'].encode('utf-8').strip()
    r.wellFormed = 1
    r.parsedDate = now


def parse_feed():
    r = TPlaylist.find(PIDS_QUERY)
    pool = Pool(size=32)
    now = dt.datetime.now()

    def f(r):
        pid = r.pid
        feed_key = 'feed_%d' % (pid)
        cr = TCache.find_one({'key': feed_key})
        if not cr:
            print('FEED NOT EXISTED. pid = %d' % (pid))
            return
        if not FORCE_PARSE_FEED and r.parsedDate and r.parsedDate >= cr.updateDate:
            # print('PARSE FEED CACHED. pid = %d' % (pid))
            return
        print('PARSE FEED. pid = %d' % (pid))
        value = cr.value
        try:
            extract_detail(r, now, value)
        except Exception as e:
            print('PARSE FEED FAILED. error = %s' % (e))
            return
        TPlaylist.update_one({'pid': pid}, r)

    for r in rs:
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    print('PARSE FEED DONE')

if __name__ == '__main__':
    create_table()
    # copy_cache()
    collect_genres()
    comb = make_combination()
    if 'index' in sys.argv:
        down_index(comb)
        parse_index(comb)
    if 'lookup' in sys.argv:
        down_lookup()
        parse_lookup()
    if 'feed' in sys.argv:
        down_feed()
        parse_feed()
