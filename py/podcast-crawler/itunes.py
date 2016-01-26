#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from util import *

import os
import time
import re
import random
import datetime as dt
import json as json_lib
import xml.dom.minidom

from bs4 import BeautifulSoup
import gevent
from gevent.pool import Pool


def make_comb(shuffle=False):
    comb = []
    for country in ITUNES_COUNTRY_CODE.values():
        if country.find('_') != -1:
            continue
        # for genre in ITUNES_PODCAST_GENRE_CODE.values():
        for genre in ITUNES_PODCAST_ALL_GENRE_CODE.values():
            comb.append((country, genre))
    if shuffle:
        random.shuffle(comb)
    else:
        comb.sort(lambda x, y: cmp(x[0], y[0]))
    return comb


def down_index(comb, force=False):
    pool = Pool(size=8)
    URL = 'http://itunes.apple.com/%s/genre/id%d?mt=2'
    if USE_HTTPS:
        URL = URL.replace('http://', 'https://')
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=INDEX_CACHE_EXPIRE_DAYS)

    print('DOWN INDEX ...')
    for (country, genre) in comb:
        def f(country, genre):
            index_key = 'idx_%s_%d' % (country, genre)
            offset = hash(index_key) % (INDEX_CACHE_EXPIRE_DAYS / 2)
            cr = TCache.find_one({'key': index_key})
            if not force and cr and cr['updateDate'] > (expireDate + dt.timedelta(days=offset)):
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


def parse_index(comb, force=False):
    print('PARSE INDEX ...')
    for (country, genre) in comb:
        index_key = 'idx_%s_%d' % (country, genre)
        r = TCache.find_one({'key': index_key})
        if not r:
            print('INDEX NOT EXISTED. (%s, %d)' % (country, genre))
            continue
        data = r['value']
        bs = BeautifulSoup(data)
        pds = bs.select('div[id="selectedcontent"] ul li a')
        print('PARSE INDEX (%s, %d)' % (country, genre))
        pids = set()
        itunes_ids = set()
        for pd in pds:
            # to guarantee utf-8.
            title = pd.get_text().encode('utf-8')
            link = pd.attrs['href']
            try:
                m = re.search(r'/id(\d+)\?', link)
                pid = int(m.groups(1)[0])
            except:
                print('PARSE INDEX FAILED. link = %s' % (link))
                continue
            # print(link, pid)
            if pid in pids:
                continue
            pids.add(pid)
            r = TPlaylist.find_one({'pid': pid})
            if not force and r:
                continue
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
    print('PARSE INDEX DONE.')


def down_lookup(force=False):
    pids = TPlaylist.find(PIDS_QUERY, projection=('pid',))
    pool = Pool(size=4)
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=LOOKUP_CACHE_EXPIRE_DAYS)

    URL = 'http://itunes.apple.com/lookup?id=%d'
    if USE_HTTPS:
        URL = URL.replace('http://', 'https://')
    print('DOWN LOOKUP ...')

    def f(pid):
        lookup_key = 'lkp_%d' % (pid)
        offset = hash(lookup_key) % (LOOKUP_CACHE_EXPIRE_DAYS / 2)
        cr = TCache.find_one({'key': lookup_key})
        if not force and cr and cr['updateDate'] > (expireDate + dt.timedelta(days=offset)):
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
    """collect geners in different languages."""
    URL = 'http://itunes.apple.com/%s/genre/id26?mt=2'
    if USE_HTTPS:
        URL = URL.replace('http://', 'https://')
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
        bs = BeautifulSoup(data)
        rs = bs.select('#genre-nav > div > ul > li > ul > li > a')
        rs2 = bs.select('#genre-nav > div > ul > li > a')
        gs = {}
        for r in rs + rs2:
            link = r.attrs['href']
            m = re.search(rex, link)
            gid = int(m.groups(1)[0])
            text = r.get_text().encode('utf-8')
            gs[gid] = text
        store[country] = gs
    with open('genres_all.json', 'w') as fh:
        json_lib.dump(store, fh)
    store2 = {}
    for (country, genres) in store.items():
        store2[country] = {v: genres[v]
                           for v in ITUNES_PODCAST_GENRE_CODE.values()}
    with open('genres.json', 'w') as fh:
        json_lib.dump(store2, fh)


def parse_lookup(force=False):
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
            r.comment = 'ELOOKUP'
            TPlaylist.replace_one({'pid': pid}, r.to_json())
            return
        data = json['results'][0]
        if 'feedUrl' not in data:
            r.skip = 1
            r.comment = 'ENOFEED'
            TPlaylist.replace_one({'pid': pid}, r.to_json())
            return
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
        if 'skip' in r:
            continue
        if not force and 'feedUrl' in r:
            continue
        r = Document.from_json(r)
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    print('PARSE LOOKUP DONE.')


def down_trend(comb, just_all=False):
    pool = Pool(size=4)
    URL = 'http://itunes.apple.com/%s/rss/toppodcasts/limit=100/genre=%d/xml'
    URL_ALL = 'http://itunes.apple.com/%s/rss/toppodcasts/limit=100/xml'
    if USE_HTTPS:
        URL = URL.replace('http://', 'https://')
        URL_ALL = URL_ALL.replace('http://', 'https://')
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=TREND_CACHE_EXPIRE_DAYS)
    print('DOWN TREND ...')
    for (country, genre) in comb:
        def f(country, genre):
            trend_key = 'trd_%s_%d' % (country, genre)
            cr = TCache.find_one({'key': trend_key})
            if cr and cr['updateDate'] > expireDate:
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
                return
            value = res.content
            if cr:
                cache = cr
            else:
                cache = {'key': trend_key,
                         'tag': 'trend'}
            cache['value'] = value
            cache['updateDate'] = now
            TCache.replace_one({'key': trend_key}, cache, upsert=True)
            time.sleep(1)
        if not just_all:
            g = gevent.spawn(f, country, genre)
            pool.add(g)
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
        x = entry.getElementsByTagName('title')[0]
        title = x.firstChild.data.encode('utf-8')
        pids.append((pid, title))
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
            for (idx, xpid) in enumerate(pids):
                (pid, title) = xpid
                r = TPlaylist.find_one({'pid': pid})
                if not r:
                    print('PARSE TREND PID NOT EXISTED. pid = %d' % (pid))
                    r = {'pid': pid,
                         'country': [country],
                         'genres': [],
                         'weight': 0.0,
                         'title': title}
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
                TPlaylist.replace_one({'pid': pid}, r, upsert=True)
        g = gevent.spawn(f, country, genre)
        pool.add(g)
        pass
    for country in ITUNES_COUNTRY_CODE.values():
        if country.find('_') != -1:
            continue
        g = gevent.spawn(f, country, 0)
        pool.add(g)
    pool.join()
    print('PARSE TREND DONE')


def top_titles(comb):
    down_trend(comb, just_all=True)
    print('TOP TITLES ...')
    results = []
    for (name, country) in ITUNES_COUNTRY_CODE.items():
        if country.find('_') != -1:
            continue
        rs = []
        trend_key = 'trd_%s_%d' % (country, 0)
        cr = TCache.find_one({'key': trend_key})
        if not cr:
            print('TREND NOT EXISTED. (%s, %d)' % (country, 0))
            continue
        data = cr['value']
        print('parse country %s' % (country))
        dom = xml.dom.minidom.parseString(data)
        entries = dom.getElementsByTagName('entry')[:25]
        rs = map(lambda x: x.getElementsByTagName(
            'title')[0].firstChild.data, entries)
        results.append((name, country, rs))
    with open('top_titles.txt', 'w') as fh:
        for (name, country, rs) in results:
            fh.write('--------------------%s(%s)--------------------\n' %
                     (name, country))
            for (idx, r) in enumerate(rs):
                fh.write('%2d  %s\n' % (idx + 1, r))
    print('TOP TITLES DONE.')

if __name__ == '__main__':
    comb = make_comb()
    if '--index' in sys.argv:
        (fd, fp) = ('--force-down-index' in sys.argv,
                    '--force-parse-index' in sys.argv)
        down_index(comb, fd)
        parse_index(comb, fp)
    if '--lookup' in sys.argv:
        (fd, fp) = ('--force-down-lookup' in sys.argv,
                    '--force-parse-lookup' in sys.argv)
        down_lookup(fd)
        parse_lookup(fp)
    if '--trend' in sys.argv:
        down_trend(comb, just_all=False)
        parse_trend(comb)
    if '--topts' in sys.argv:
        top_titles(comb)
