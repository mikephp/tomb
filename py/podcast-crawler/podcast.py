#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from util import *

import datetime as dt
import traceback

import feedparser
import xml.dom.minidom
import gevent
from gevent.pool import Pool

FORCE_ALL = 2
FORCE_PARSE = 1


def check_feed(force):
    # to avoid exception of CursorNotFound.
    rs = TPlaylist.find(PIDS_QUERY, projection=(
        'feedUrl',), no_cursor_timeout=True)
    pool = Pool(size=8)
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=FEED_CACHE_EXPIRE_DAYS)

    print('CHECK FEED ...')
    ctx = {'skip': 0,
           'cache': 0,
           'econn': 0,
           'total': 0}
    for r in rs:
        if 'feedUrl' not in r:
            continue
        url = r['feedUrl']
        ctx['total'] += 1
        g = gevent.spawn(down_feed, ctx, url, now, expireDate, force)
        pool.add(g)
    pool.join()
    print('CHECK FEED ctx = {}'.format(ctx))
    print('CHECK FEED DONE.')


def skip(r, comment):
    r.skip = 1
    r.comment = comment
    TCache.replace_one({'key': r.key}, r.to_json(), upsert=True)


def down_feed(ctx, url, now, expireDate, force):
    feed_key = get_feed_key(url)
    cr = TCache.find_one({'key': feed_key})
    # 如果缓存存在并且'skip'的话，说明这个源其实是存在问题的. 直接忽略
    if cr and cr.get('skip', 0):
        # print('DOWN FEED SKIP. url = %s' % (url))
        ctx['skip'] += 1
        return

    if force == FORCE_PARSE and cr and 'value' in cr:
        parse_feed(url, cr['value'], now)
        return

    # 如果cache没有过期的话也忽略
    if not force and cr and 'updateDate' in cr and cr['updateDate'] > expireDate:
        # print('DOWN FEED CACHED. url = %s' % (url))
        ctx['cache'] += 1
        return

    if cr:
        r = Document.from_json(cr)
    else:
        r = Document.from_json({'key': feed_key,
                                'tag': 'feed',
                                'url': url})
    print('DOWN FEED. url = %s' % (url))

    # 通过HTTP头部来判断是否可以Cache.
    headers = getattr(r, 'headers', {})
    r.headers = headers
    try:
        res = requests.head(url, timeout=10, headers=headers)
    except:
        # print('DOWN FEED FAILED. CONNECTION ERROR. url = %s' % (url))
        ctx['econn'] += 1
        skip(r, 'ECONN')
        return
    # HTTP Not Modified or Content-Length is same.
    # TODO: 301. redirect.
    if res.status_code == 304 or \
            headers.get('Content-Length', '') == r.headers.get('Content-Length', 'X'):
        print('DOWN FEED OK. NOT MODIFIED. url = %s' % (url))
        r.updateDate = now
        TCache.replace_one({'key': r.key}, r.to_json(), upsert=True)
        return
    if res.status_code != 200:
        print('DOWN FEED FAILED. url = %s code = %d' % (url, res.status_code))
        code = res.status_code
        skip(r, 'E%d' % (code))
        return
    if int(r.headers.get('Content-Length', 0)) > MAX_FEED_SIZE:
        print('DOWN FEED FAILED. url = %s size = %d' %
              (url, int(r.headers.get('Content-Length', 0))))
        skip(r, 'EBIG')
        return

    # otherwise we can download it.
    try:
        res = requests.get(url, timeout=10)
    except:
        # print('DOWN FEED FAILED. CONNECTION ERROR. url = %s' % (url))
        ctx['econn'] += 1
        skip(r, 'ECONN')
        return
    if res.status_code != 200:
        print('DOWN FEED FAILED. url = %s code = %d' % (url, res.status_code))
        code = res.status_code
        skip(r, 'E%d' % (code))
        return
    value = res.content

    # unicode decode error.
    try:
        value = value.encode('utf-8')
    except:
        print('DOWN FEED FAILED. url = %s not utf-8' % (url))
        skip(r, 'EUTF8')
        return
    if len(value) > MAX_FEED_SIZE:
        print('DOWN FEED FAILED. url = %s size = %d' % (url, len(value)))
        skip(r, 'EBIG')
        return
    r.value = value
    r.updateDate = now
    r.releaseDate = now
    if 'Last-Modified' in res.headers:
        r.headers['If-Modified-Since'] = res.headers['Last-Modified']
    if 'ETag' in res.headers:
        r.headers['If-None-Match'] = res.headers['ETag']
    if 'Content-Length' in res.headers:
        r.headers['Content-Length'] = res.headers['Content-Length']
    parse_feed(url, value, now)
    TCache.replace_one({'key': r.key}, r.to_json(), upsert=True)


def extract_detail(r, data):
    dom = feedparser.parse(data)
    feed = dom['feed']
    r.language = feed.get('language', '').encode('utf-8')
    r.title = feed.get('title', '').encode('utf-8')
    description = feed.get('summary', '') or feed.get('description', '')
    r.description = description.encode('utf-8')
    r.author = feed.get('author', '').encode('utf-8')
    r.releaseDate = dom.entries[0].published
    r.trackCount = len(dom.entries)
    r.cover = feed.image.href if 'image' in feed and 'href' in feed.image else ""
    r.parsed = 1


def parse_feed(url, value, now):
    print('PARSE FEED. url = %s' % (url))
    feed_key = get_feed_key(url)
    r = TPodcast.find_one({'key': feed_key})
    if not r:
        r = {'key': feed_key,
             'feedUrl': url}
    r = Document.from_json(r)
    try:
        extract_detail(r, value)
        r.parsedDate = now
    except Exception as e:
        print('PARSE FEED FAILED. url = %s' % (url))
        # traceback.print_exc()
        return
    TPodcast.replace_one({'key': feed_key}, r.to_json(), upsert=True)


def back_fill_itunes(force):
    rs = TPlaylist.find(PIDS_QUERY)
    pool = Pool(size=8)
    print('BACK FILL ITUNES ...')

    def f(r):
        url = r.feedUrl
        feed_key = get_feed_key(url)
        r2 = TPodcast.find_one({'key': feed_key})
        if not r2:
            # print('BACK FILL ITUNES. Podcast not found. url = %s feed_key = %s' %
            #       (url, feed_key))
            r2 = {'key': feed_key,
                  'feedUrl': url}
        r2 = Document.from_json(r2)
        if not force and getattr(r2, 'itunes_id', 0):
            # print('BACK FILL ITUNES. Podcast cached.')
            return
        r2.itunes_id = r.pid
        r2.itunes_cover = getattr(r, 'cover30', '')
        country = getattr(r2, 'country', [])
        for x in r.country:
            if x not in country:
                country.append(x)
        r2.country = country
        genres = getattr(r2, 'genres', [])
        for x in r.genres:
            if x not in genres:
                genres.append(x)
        r2.genres = genres
        r2.title = getattr(r2, 'title', '') or getattr(r, 'title', '')
        r2.author = getattr(r2, 'author', '') or getattr(r, 'authorName', '')
        r2.trackCount = getattr(
            r2, 'trackCount', 0) or getattr(r, 'trackCount', 0)
        r2.releaseDate = getattr(
            r2, 'releaseDate', '') or getattr(r, 'releaseDate', '')
        TPodcast.replace_one({'key': feed_key}, r2.to_json(), upsert=True)
    for r in rs:
        if 'feedUrl' not in r:
            continue
        r = Document.from_json(r)
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    print('BACK FILL ITUNES DONE')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    args = ['--feed', '--force', '--force-only-parse',
            '--back-fill']
    for arg in args:
        parser.add_argument(arg, action='store_true')
    args = parser.parse_args()

    force = 0
    if args.force:
        force = FORCE_ALL
    if args.force_only_parse:
        force = FORCE_PARSE

    if args.feed:
        check_feed(force)
    if args.back_fill:
        back_fill_itunes(force)
