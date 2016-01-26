#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from util import *

import hashlib
import datetime as dt

import feedparser
import xml.dom.minidom
import gevent
from gevent.pool import Pool


def skip(r, comment):
    r.skip = 1
    r.comment = comment
    TCache.replace_one({'key': r.key}, r.to_json(), upsert=True)


def down_feed(url, now, expireDate, pid=None, force=False):
    sign = str(pid)
    if not sign:
        sign = hashlib.sha1(url).hexdigest()
    feed_key = 'feed_%s' % (sign)
    cr = TCache.find_one({'key': feed_key})
    # 如果缓存存在并且'skip'的话，说明这个源其实是存在问题的
    if cr and cr.get('skip', 0):
        print('DOWN FEED SKIP. url = %s' % (url))
        return
    if not force and cr and cr['updateDate'] > expireDate:
        # print('DOWN FEED CACHED. url = %s' % (url))
        return
    if cr:
        r = Document.from_json(cr)
    else:
        r = Document.from_json({'key': feed_key,
                                'tag': 'feed'})
        # 从非itunes上来的.
        if not pid:
            r.tag = 'feed2'
            r.url = url
    print('DOWN FEED. url = %s' % (url))

    # 通过HTTP头部来判断是否可以Cache.
    headers = getattr(r, 'headers', {})
    r.headers = headers
    try:
        res = requests.head(url, timeout=10, headers=headers)
    except:
        print('DOWN FEED FAILED. CONNECTION ERROR. url = %s' % (url))
        # skip(r, 'ECONN')
        # save(r)
        return
    # HTTP Not Modified or Content-Length is same.
    if res.status_code == 304 or headers.get('Content-Length', '') == r.headers.get('Content-Length', 'X'):
        print('DOWN FEED OK. NOT MODIFIED. url = %s' % (url))
        r.updateDate = now
        TCache.replace_one({'key': r.key}, r.to_json(), upsert=True)
        return
    if res.status_code != 200:
        print('DOWN FEED FAILED. url = %s code = %d' % (url, res.status_code))
        code = res.status_code
        skip(r, 'E%d' % (code))
        return
    if int(r.headers.get('Content-Length', '0')) > MAX_FEED_SIZE:
        skip(r, 'EBIG')
        return

    # otherwise we can download it.
    try:
        res = requests.get(url, timeout=10)
    except:
        # skip(r, 'ECONN')
        # save(r)
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
        skip(r, 'EUTF8')
        return
    if len(value) > MAX_FEED_SIZE:
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
    TCache.replace_one({'key': r.key}, r.to_json(), upsert=True)


def down_feed_itunes(force=False):
    # to avoid exception of CursorNotFound.
    rs = TPlaylist.find(PIDS_QUERY, projection=(
        'feedUrl', 'pid',), no_cursor_timeout=True)
    pool = Pool(size=8)
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=FEED_CACHE_EXPIRE_DAYS)

    print('DOWN FEED ITUNES ...')
    for r in rs:
        pid = r['pid']
        if 'feedUrl' not in r:
            continue
        url = r['feedUrl']
        g = gevent.spawn(down_feed, url, now, expireDate, pid, force)
        pool.add(g)
    pool.join()
    print('DOWN FEED ITUNES DONE.')


def extract_detail(r, data, now):
    title = ""
    language = ""
    description = ""
    cover = ""
    author = ""
    releaseDate = ""
    trackCount = 0
    try:
        dom = xml.dom.minidom.parseString(data)
        d = dom.getElementsByTagName('title')
        title = d[0].firstChild.data if d else ""
        d = dom.getElementsByTagName('language')
        language = d[0].firstChild.data if d else ""
        d = dom.getElementsByTagName('itunes:summary') or dom.getElementsByTagName(
            'description')
        description = d[0].firstChild.data if d else ""
        d = dom.getElementsByTagName('itunes:image')
        cover = d[0].getAttribute('href') if d else ""
        d = dom.getElementsByTagName('itunes:author')
        author = d[0].firstChild.data if d else ""
        d = dom.getElementsByTagName('pubDate')
        releaseDate = d[0].firstChild.data if d else ""
        d = dom.getElementsByTagName('item')
        trackCount = len(d)
    except:
        d = feedparser.parse(data)
        feed = d['feed']
        language = feed.get('language', '')
        title = feed.get('title', '')
        description = feed.get('summary', '') or feed.get('description', '')
        author = feed.get('author', '')
        releaseDate = d.entries[0].published
        trackCount = len(d.entries)
        cover = feed.image.href if 'image' in feed and 'href' in feed.image else ""
    r.title = title.encode('utf-8')
    r.language = language.encode('utf-8')
    r.description = description.encode('utf-8')
    r.cover = cover
    r.author = author.encode('utf-8')
    r.releaseDate = releaseDate
    r.trackCount = trackCount
    r.parsed = 1
    r.parsedDate = now


import dateutil.parser


def parse_feed_itunes(force=False):
    rs = TPlaylist.find(PIDS_QUERY)
    pool = Pool(size=32)
    now = dt.datetime.now()

    print('PARSE FEED ITUNES ...')

    def f(r):
        pid = r.pid
        feed_key = 'feed_%d' % (pid)
        cr = TCache.find_one({'key': feed_key})
        if not cr:
            print('FEED NOT EXISTED. pid = %d' % (pid))
            return
        if 'skip' in cr and cr['skip']:
            print('FEED SKIPPED. pid = %d' % (pid))
            return
        key = hashlib.sha1(r.feedUrl).hexdigest()
        r2 = TPodcast.find_one({'key': key})
        if not r2:
            r2 = {'key': key,
                  'feedUrl': r.feedUrl,
                  'itunes_id': pid,
                  'country': r.country,
                  'genres': r.genres}
        r2 = Document.from_json(r2)
        if not force and hasattr(r2, 'parsedDate') and r2.parsedDate >= cr['releaseDate']:
            # print('PARSE FEED ITUNES CACHED. url = %s' % (r.feedUrl))
            return
        print('PARSE FEED ITUNES. url = %s' % (r.feedUrl))
        value = cr['value']
        try:
            extract_detail(r2, value, now)
        except Exception as e:
            print('PARSE FEED FAILED. error = %s' % (e))
            return
        for x in r.country:
            if not x in r2.country:
                r2.country.append(x)
        for x in r.genres:
            if not x in r2.genres:
                r2.genres.append(x)
        TPodcast.replace_one({'key': r2.key}, r2.to_json(), upsert=True)

    for r in rs:
        if 'feedUrl' not in r:
            continue
        r = Document.from_json(r)
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    print('PARSE FEED ITUNES DONE.')

if __name__ == '__main__':
    if '--feed' in sys.argv:
        (fd, fp) = ('--force-down-feed-itunes' in sys.argv,
                    '--force-parse-feed-itunes' in sys.argv)
        down_feed_itunes(fd)
        parse_feed_itunes(fp)
