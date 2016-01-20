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

Client = MongoClient(MONGO_URL)
DB = Client.pdcast
TCache = DB['cache']
TPlaylist = DB['playlist']

from requests.adapters import HTTPAdapter
Session = requests.Session()
Session.mount('http://', HTTPAdapter(max_retries=MAX_RETRY_NUMBER))
Session.mount('https://', HTTPAdapter(max_retries=MAX_RETRY_NUMBER))


class Document(object):

    @classmethod
    def from_json(cls, js):
        x = cls()
        x.__dict__ = js
        return x

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
        for genre in ITUNES_PODCAST_ALL_GENRE_CODE.values():
            # for genre in ITUNES_PODCAST_GENRE_CODE.values(): # to bootstrap
            comb.append((country, genre))
    if shuffle:
        random.shuffle(comb)
    else:
        comb.sort(lambda x, y: cmp(x[0], y[0]))
    return comb


def down_index(comb):
    pool = Pool(size=8)
    URL = 'http://itunes.apple.com/%s/genre/id%d?mt=2'
    if USE_HTTPS:
        URL = 'https://itunes.apple.com/%s/genre/id%d?mt=2'
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=INDEX_CACHE_EXPIRE_DAYS)

    print('DOWN INDEX ...')
    for (country, genre) in comb:
        def f(country, genre):
            index_key = 'idx_%s_%d' % (country, genre)
            cr = TCache.find_one({'key': index_key})
            if not FORCE_DOWN_INDEX and cr and cr['updateDate'] > expireDate:
                # print('DOWN INDEX CACHED. (%s, %d)' % (country, genre))
                return

            print('DOWN INDEX. (%s, %d)' % (country, genre))
            url = URL % (country, genre)
            res = requests.get(url)
            if res.status_code != 200:
                print('DOWN INDEX FAILED. url = %s code = %d' %
                      (url, res.status_code))
                return
            value = res.content
            if cr:
                cache = cr
            else:
                cache = {'key': index_key,
                         'tag': 'index'}
            cache['value'] = value
            cache['updateDate'] = now
            TCache.replace_one({'key': index_key}, cache, upsert=True)
        g = gevent.spawn(f, country, genre)
        pool.add(g)
    pool.join()
    print('DOWN INDEX DONE.')


def parse_index_1(country, genre):
    index_key = 'idx_%s_%d' % (country, genre)
    r = TCache.find_one({'key': index_key})
    if not r:
        print('INDEX NOT EXISTED. (%s, %d)' % (country, genre))
        return
    data = r['value']
    bs = BeautifulSoup(data, "lxml")
    pds = bs.select('div[id="selectedcontent"] ul li a')
    print('PARSE INDEX (%s, %d)' % (country, genre))
    pids = set()
    for pd in pds:
        title = pd.get_text().encode('utf-8')
        link = pd.attrs['href']
        m = re.search(r'/id(\d+)\?', link)
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
            r = Document.from_json({'pid': pid,
                                    'country': [country],
                                    'genres': [genre],
                                    'weight': 0.0,
                                    'title': title})
            TPlaylist.insert_one(r.to_json())
        else:
            r = Document.from_json(r)
            r.title = title
            if not country in r.country:
                r.country.append(country)
            if not genre in r.genres:
                r.genres.append(genre)
            TPlaylist.replace_one({'pid': pid}, r.to_json())


def parse_index(comb):
    print('PARSE INDEX ...')
    for (country, genre) in comb:
        parse_index_1(country, genre)
    print('PARSE INDEX DONE.')


def down_lookup():
    pids = TPlaylist.find(PIDS_QUERY, projection=('pid',))
    pool = Pool(size=4)
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=LOOKUP_CACHE_EXPIRE_DAYS)

    URL = 'http://itunes.apple.com/lookup?id=%d'
    if USE_HTTPS:
        URL = 'https://itunes.apple.com/lookup?id=%d'
    print('DOWN LOOKUP ...')

    def f(pid):
        lookup_key = 'lkp_%d' % (pid)
        cr = TCache.find_one({'key': lookup_key})
        if not FORCE_DOWN_LOOKUP and cr and cr['updateDate'] > expireDate:
            # print('DOWN LOOKUP CACHED. pid = %d' % (pid))
            return
        print('DOWN LOOKUP. pid = %d' % pid)
        url = URL % (pid)
        res = requests.get(url)
        if res.status_code != 200:
            print("DOWN LOOKUP FAILED. url = %s code = %d" %
                  (url, res.status_code))
            return
        value = res.content
        if cr:
            cache = cr
        else:
            cache = {'key': lookup_key,
                     'tag': 'lookup'}
        cache['value'] = value
        cache['updateDate'] = now
        TCache.replace_one({'key': lookup_key}, cache, upsert=True)
        time.sleep(1)

    for pid in pids:
        g = gevent.spawn(f, pid['pid'])
        pool.add(g)
    pool.join()
    print('DOWN LOOKUP DONE.')


def collect_genres():
    store = {}
    pids = TPlaylist.find(PIDS_QUERY, projection=('pid', ))
    pool = Pool(size=8)

    print('COLLECT GENRES ...')

    def f(pid):
        lookup_key = 'lkp_%d' % (pid)
        cr = TCache.find_one({'key': lookup_key})
        if not cr:
            print('LOOKUP NOT EXISTED. pid = %d' % (pid))
            return
        json = json_lib.loads(cr['value'])
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
            # if genre == 'Islam':
            #     print(pid)
            store[genre] = genreId

    for pid in pids:
        g = gevent.spawn(f, pid['pid'])
        pool.add(g)
    pool.join()
    print(store)
    print('COLLECT GENRES DONE.')

import os


def collect_genres2():
    URL = 'http://itunes.apple.com/%s/genre/id26?mt=2'
    if USE_HTTPS:
        URL = 'https://itunes.apple.com/%s/genre/id26?mt=2'
    store = {}
    if not os.path.exists('cache'):
        os.mkdir('cache')
    rex = re.compile(r'id(\d+)\?')
    for country in ITUNES_COUNTRY_CODE.values():
        if country.find('_') != -1:
            continue
        fname = 'cache/genre-%s.list' % (country)
        if not os.path.exists(fname):
            r = requests.get(URL % country)
            data = r.content
            with open(fname, 'w') as fh:
                fh.write(data)
        else:
            data = open(fname).read()
        bs = BeautifulSoup(data, "lxml")
        rs = bs.select('#genre-nav > div > ul > li > ul > li > a')
        gs = {}
        for r in rs:
            link = r.attrs['href']
            m = re.search(rex, link)
            gid = int(m.groups(1)[0])
            text = r.get_text().encode('utf-8')
            gs[gid] = text
        store[country] = gs
    with open('genres.json', 'w') as fh:
        json_lib.dump(store, fh)


def parse_lookup():
    rs = TPlaylist.find(PIDS_QUERY)
    pool = Pool(size=32)

    print('PARSE LOOKUP ...')

    def f(r):
        pid = r.pid
        lookup_key = 'lkp_%d' % (pid)
        cr = TCache.find_one({'key': lookup_key})
        if not cr:
            print('LOOKUP NOT EXISTED. pid = %d' % (pid))
            return
        print('PARSE LOOKUP. pid = %d' % (pid))
        # validate json data.
        json = json_lib.loads(cr['value'])
        if json['resultCount'] != 1:
            if json['resultCount'] != 0:
                print('PARSE LOOKUP FAILED. result count %d. pid = %d' %
                      (json['resultCount'], pid))
            r.skip = 1
            TPlaylist.replace_one({'pid': pid}, r.to_json())
            return
        data = json['results'][0]
        genreIds = map(lambda x: int(x), data['genreIds'])
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
        for x in genreIds:
            if not x in r.genres:
                r.genres.append(x)
        TPlaylist.replace_one({'pid': pid}, r.to_json())

    for r in rs:
        r = Document.from_json(r)
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    print('PARSE LOOKUP DONE.')


def down_feed():
    # pymongo.errors.CursorNotFound
    rs = TPlaylist.find(PIDS_QUERY, no_cursor_timeout=True)
    pool = Pool(size=8)
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=FEED_CACHE_EXPIRE_DAYS)

    print('DOWN FEED ...')

    def skip_it(r, comment):
        r.skip = 1
        r.comment = comment
        TPlaylist.replace_one({'pid': r.pid}, r.to_json())

    def f(r):
        if hasattr(r, 'skip') and r.skip:
            return
        pid = r.pid
        feed_key = 'feed_%d' % (pid)
        cr = TCache.find_one({'key': feed_key})
        if not FORCE_DOWN_INDEX and cr and cr['updateDate'] > expireDate:
            # print('DOWN FEED CACHED. pid = %d' % pid)
            return
        url = r.feedUrl
        print('DOWN FEED. pid = %d. url = %s' % (pid, url))
        try:
            res = requests.get(url, timeout=10)
        except:
            print('DOWN FEED FAILED. CONNECTION ERROR. pid = %d, url = %s' %
                  (pid, url))
            skip_it(r, 'ECONN')
            return
        if res.status_code != 200:
            print('DOWN FEED FAILED. pid = %d, url = %s code = %d' %
                  (pid, url, res.status_code))
            if res.status_code in (403, 404):
                skip_it(r, 'E404')
            return
        value = res.content
        # unicode decode error.
        try:
            value = value.encode('utf-8')
        except:
            skip_it(r, 'EUTF8')
            return

        if len(value) > (1 << 20):
            skip_it(r, 'EBIG')
            return
        if cr:
            cache = cr
        else:
            cache = {'key': feed_key,
                     'tag': 'feed'}
        cache['value'] = value
        cache['updateDate'] = now
        TCache.replace_one({'key': feed_key}, cache, upsert=True)

    for r in rs:
        r = Document.from_json(r)
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    print('DOWN FEED DONE.')


import feedparser
import xml.dom.minidom


def extract_detail(r, now, data):
    language = ""
    description = ""
    try:
        dom = xml.dom.minidom.parseString(data)
        d = dom.getElementsByTagName(
            'description') or dom.getElementsByTagName('itunes:summary')
        if d:
            description = d[0].firstChild.data
        d = dom.getElementsByTagName('language')
        if d:
            language = d[0].firstChild.data
    except:
        d = feedparser.parse(data)
        feed = d['feed']
        if 'description' in feed:
            description = feed['description']
        if 'summary' in feed:
            description = feed['summary']
        if 'language' in feed:
            language = feed['language']
    if not isinstance(description, str) and not isinstance(description, unicode):
        print('EXTRACT DETAIL. description not string but %s' %
              (type(description)))
    if not isinstance(language, str) and not isinstance(language, unicode):
        print('EXTRACT DETAIL. language not string but %s' % (type(language)))
    r.description = description.encode('utf-8')
    r.language = language.encode('utf-8')
    r.wellFormed = 1
    r.parsedDate = now


def parse_feed():
    rs = TPlaylist.find(PIDS_QUERY)
    pool = Pool(size=32)
    now = dt.datetime.now()

    print('PARSE FEED ...')

    def f(r):
        pid = r.pid
        feed_key = 'feed_%d' % (pid)
        cr = TCache.find_one({'key': feed_key})
        if not cr:
            print('FEED NOT EXISTED. pid = %d' % (pid))
            return
        if not FORCE_PARSE_FEED and hasattr(r, 'parsedDate') and r.parsedDate >= cr['updateDate']:
            # print('PARSE FEED CACHED. pid = %d' % (pid))
            return
        print('PARSE FEED. pid = %d' % (pid))
        value = cr['value']
        try:
            extract_detail(r, now, value)
        except Exception as e:
            print('PARSE FEED FAILED. error = %d' % (e))
            return
        TPlaylist.replace_one({'pid': pid}, r.to_json())

    for r in rs:
        r = Document.from_json(r)
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    print('PARSE FEED DONE.')


def down_trend(comb):
    pool = Pool(size=8)
    URL = 'http://itunes.apple.com/%s/rss/toppodcasts/limit=100/genre=%d/xml'
    URL_ALL = 'http://itunes.apple.com/%s/rss/toppodcasts/limit=100/xml'
    if USE_HTTPS:
        URL = 'https://itunes.apple.com/%s/rss/toppodcasts/limit=100/genre=%d/xml'
        URL_ALL = 'https://itunes.apple.com/%s/rss/toppodcasts/limit=100/xml'
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=TREND_CACHE_EXPIRE_DAYS)

    print('DOWN TREND ...')
    for (country, genre) in comb:
        def f(country, genre):
            trend_key = 'trd_%s_%d' % (country, genre)
            cr = TCache.find_one({'key': trend_key})
            if not FORCE_DOWN_TREND and cr and cr['updateDate'] > expireDate:
                # print('DOWN TREND CACHED. (%s, %d)' % (country, genre))
                return
            print('DOWN TREND. (%s, %d)' % (country, genre))
            if genre == 0:  # so special.
                url = URL_ALL % (country)
            else:
                url = URL % (country, genre)
            res = requests.get(url)
            if res.status_code != 200:
                print('DOWN TREND FAILED. url = %s code = %d' % (
                    url, res.status_code))
            value = res.content
            if cr:
                cache = cr
            else:
                cache = {'key': trend_key,
                         'tag': 'trend'}
            cache['value'] = value
            cache['updateDate'] = now
            TCache.replace_one({'key': trend_key}, cache, upsert=True)
        g = gevent.spawn(f, country, genre)
        pool.add(g)
        pass
    for country in ITUNES_COUNTRY_CODE.values():
        if country.find('_') != -1:
            continue
        g = gevent.spawn(f, country, 0)
        pool.add(g)
    pool.join()
    print('DOWN TREND DONE.')


def extract_pids(data):
    dom = xml.dom.minidom.parseString(data)
    entries = dom.getElementsByTagName('entry')
    pids = []
    for entry in entries:
        x = entry.getElementsByTagName('id')[0]
        pid = int(x.getAttribute('im:id'))
        pids.append(pid)
    return pids


def parse_trend(comb):
    pool = Pool(size=32)
    decay = 0.75

    print('PARSE TREND ...')
    for (country, genre) in comb:
        def f(country, genre):
            trend_key = 'trd_%s_%d' % (country, genre)
            cr = TCache.find_one({'key': trend_key})
            if not cr:
                print('TREND NOT EXISTED. (%s, %d)' % (country, genre))
                return
            data = cr['value']
            pids = extract_pids(data)
            pids = pids[::-1]
            gs = str(genre)
            for (idx, pid) in enumerate(pids):
                r = TPlaylist.find_one({'pid': pid})
                if not r:
                    print('PARSE TREND PID NOT EXISTED. pid = %d' % (pid))
                    continue
                if not 'gw' in r:
                    r['gw'] = {}
                if not gs in r['gw']:
                    r['gw'][gs] = 0.0
                if not '0' in r['gw']:
                    r['gw']['0'] = 0.0
                weight = 1.05 ** (idx + 1) * decay / (1.05 * 100)
                weight += r['gw'][gs] * (1 - decay)
                r['gw'][gs] = weight
                w = 0.0
                sz = len(r['gw'])
                for k in r['gw'].keys():
                    if k == '0':
                        w += r['gw'][k] * 0.6
                    else:
                        w += r['gw'][k] * 0.4 / (sz - 1)
                r['weight'] = w
                TPlaylist.replace_one({'pid': pid}, r)
        g = gevent.spawn(f, country, genre)
        pool.add(g)
        pass
    for country in ITUNES_COUNTRY_CODE.values():
        if country.find('_') != -1:
            continue
        g = gevent.spawn(f, country, 0)
        pool.add(g)
    pool.join()

    # results = []
    # for (name, country) in ITUNES_COUNTRY_CODE.items():
    #     if country.find('_') != -1:
    #         continue
    #     rs = []
    #     trend_key = 'trd_%s_%d' % (country, 0)
    #     cr = TCache.find_one({'key': trend_key})
    #     if not cr:
    #         print('TREND NOT EXISTED. (%s, %d)' % (country, 0))
    #         continue
    #     data = cr['value']
    #     print('parse country %s' % (country))
    #     dom = xml.dom.minidom.parseString(data)
    #     entries = dom.getElementsByTagName('entry')[:25]
    #     rs = map(lambda x: x.getElementsByTagName(
    #         'title')[0].firstChild.data, entries)
    #     results.append((name, country, rs))
    # with open('output.txt', 'w') as fh:
    #     for (name, country, rs) in results:
    #         fh.write('--------------------%s(%s)--------------------\n' %
    #                  (name, country))
    #         for (idx, r) in enumerate(rs):
    #             fh.write('%2d  %s\n' % (idx + 1, r))

    print('PARSE TREND DONE.')

if __name__ == '__main__':
    create_table()
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
    if 'genres' in sys.argv:
        # collect_genres()
        collect_genres2()
    if 'trend' in sys.argv:
        down_trend(comb)
        parse_trend(comb)
