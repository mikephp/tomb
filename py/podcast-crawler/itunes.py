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
import mmh3

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


def check_index(comb, force):
    pool = Pool(size=8)
    URL = 'http://itunes.apple.com/%s/genre/id%d?mt=2'
    if USE_HTTPS:
        URL = URL.replace('http://', 'https://')
    now = dt.datetime.now()

    print('CHECK INDEX ...')

    def down(country, genre):
        index_key = 'idx_%s_%d' % (country, genre)
        url = URL % (country, genre)
        fetch_from_network(
            url, index_key, 'index', now, INDEX_CACHE_EXPIRE_DAYS,
            force, parse, country, genre)
        time.sleep(0.1)

    def parse(data, country, genre):
        print('PARSE INDEX (%s, %d)' % (country, genre))
        bs = BeautifulSoup(data)
        pds = bs.select('div[id="selectedcontent"] ul li a')
        pids = set()
        itunes_ids = set()
        ops = []
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
            if not r:
                r = Document.from_json({'pid': pid,
                                        'country': [country],
                                        'genres': [genre],
                                        'title': title})
                ops.append(InsertOne(r.to_json()))
            elif 'PATCH' in os.environ:
                return
            else:
                r = Document.from_json(r)
                r.title = title
                if not country in r.country:
                    r.country.append(country)
                if not genre in r.genres:
                    r.genres.append(genre)
                ops.append(ReplaceOne({'pid': pid}, r.to_json()))
        if ops:
            TPlaylist.bulk_write(ops)
        else:
            print('PARSE INDEX FAILED. NO OPS. (%s, %d)' % (country, genre))
    for (country, genre) in comb:
        pool.spawn(down, country, genre)
    pool.join()
    print('CHECK INDEX DONE.')


def check_lookup(force):
    rs = TPlaylist.find(PIDS_QUERY)
    pool = Pool(size=4)
    URL = 'http://itunes.apple.com/lookup?id=%d'
    if USE_HTTPS:
        URL = URL.replace('http://', 'https://')
    now = dt.datetime.now()

    print('CHECK LOOKUP ...')

    def down(r):
        pid = r.pid
        lookup_key = 'lkp_%d' % (pid)
        url = URL % pid
        fetch_from_network(
            url, lookup_key, 'lookup', now, LOOKUP_CACHE_EXPIRE_DAYS,
            force, parse, r)
        time.sleep(0.1)

    def parse(data, r):
        pid = r.pid
        print('PARSE LOOKUP. pid = %d' % (pid))
        if 'PATCH' in os.environ and not hasattr(r, 'skip') and hasattr(r, 'feedUrl'):
            return
        json = json_lib.loads(data)
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
        r = Document.from_json(r)
        pool.spawn(down, r)
    pool.join()
    print('CHECK LOOKUP DONE.')


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


def check_trend(comb, force, just_all=False):
    pool = Pool(size=4)
    URL = 'http://itunes.apple.com/%s/rss/toppodcasts/limit=100/genre=%d/xml'
    URL_ALL = 'http://itunes.apple.com/%s/rss/toppodcasts/limit=100/xml'
    if USE_HTTPS:
        URL = URL.replace('http://', 'https://')
        URL_ALL = URL_ALL.replace('http://', 'https://')
    now = dt.datetime.now()

    print('CHECK TREND ...')

    def down(country, genre):
        trend_key = 'trd_%s_%d' % (country, genre)
        if genre == 0:
            url = URL_ALL % (country)
        else:
            url = URL % (country, genre)
        fetch_from_network(
            url, trend_key, 'trend', now, TREND_CACHE_EXPIRE_DAYS,
            force, parse, country, genre)
        time.sleep(0.1)

    def parse(data, country, genre):
        print('PARSE TREND (%s, %d)' % (country, genre))
        pids = extract_pids(data)
        pids = pids[::-1]
        ops = []
        for (idx, xpid) in enumerate(pids):
            (pid, title) = xpid
            r = TPlaylist.find_one({'pid': pid})
            if r:
                continue
            print('PARSE TREND PID NOT EXISTED. pid = %d' % (pid))
            r = {'pid': pid,
                 'country': [country],
                 'genres': [] if genre == 0 else [genre],
                 'title': title}
            ops.append(InsertOne(r))
        if ops:
            TPlaylist.bulk_write(ops)

    if not just_all:
        for (country, genre) in comb:
            pool.spawn(down, country, genre)
    for country in ITUNES_COUNTRY_CODE.values():
        if country.find('_') != -1:
            continue
        pool.spawn(down, country, 0)
    pool.join()
    print('CHECK TREND DONE.')


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


def top_titles(comb):
    print('TOP TITLES ...')
    check_trend(comb, 0, just_all=True)
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
    import argparse
    parser = argparse.ArgumentParser()
    args = ['--index', '--trend', '--lookup', '--force']
    for arg in args:
        parser.add_argument(arg, action='store_true')

    args = parser.parse_args()
    comb = make_comb()
    force = args.force

    if args.index:
        check_index(comb, force)
    if args.trend:
        check_trend(comb, force, just_all=False)
    if args.lookup:
        check_lookup(force)
