#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from util import *
import itunes

import gevent
from gevent.pool import Pool


def setup():
    TWeight.drop()


def fill_itunes_weight():
    pool = Pool(size=32)
    print('FILL ITUNES WEIGHT ...')
    comb = itunes.make_comb()
    for (country, genre) in comb:
        def f(country, genre):
            trend_key = 'trd_%s_%d' % (country, genre)
            field = 'iw_%s_%d' % (country, genre)
            cr = TCache.find_one({'key': trend_key})
            if not cr:
                print('ITUNES TREND NOT EXISTED. (%s, %d)' % (country, genre))
                return
            data = cr['value']
            pids = itunes.extract_pids(data)
            pids = pids[::-1]
            for (idx, xpid) in enumerate(pids):
                (pid, title) = xpid
                r = TPlaylist.find_one({'pid': pid})
                if not r or 'feedUrl' not in r:
                    continue
                url = r['feedUrl']
                feed_key = get_feed_key(url)
                r2 = TWeight.find_one({'key': feed_key})
                if not r2:
                    r2 = {'key': feed_key}
                r2[field] = (idx + 1)
                TWeight.replace_one({'key': feed_key}, r2, upsert=True)
        g = gevent.spawn(f, country, genre)
        pool.add(g)
    for country in ITUNES_COUNTRY_CODE.values():
        if country.find('_') != -1:
            continue
        g = gevent.spawn(f, country, 0)
        pool.add(g)
    pool.join()
    print('PARSE TREND DONE.')


def merge_weight():
    rs = TWeight.find({})
    pool = Pool(size=32)

    print('MERGE WEIGHT ...')

    def f(r):
        keys = r.keys()
        iw_keys = filter(lambda x: x.startswith('iw_'), keys)
        for k in iw_keys:
            fw_key = k[3:]
            r[fw_key] = r[k]
        TWeight.replace_one({'key': r['key']}, r)

    for r in rs:
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    print('MERGE WEIGHT DONE.')


def update_toplist():
    pool = Pool(size=4)
    print('UPDATE TOPLIST ...')
    comb = itunes.make_comb()
    fields = ('feedUrl', 'description', 'title',
              'author', 'cover', 'itunes_cover', 'trackCount',
              'releaseDate')
    for (country, genre) in comb:
        def f(country, genre):
            sort_field = '%s_%s' % (country, genre)
            toplist_key = sort_field
            rs = TWeight.find({}, projection=('key', ), sort = [
                              (sort_field, pymongo.DESCENDING)], limit = 200)
            docs = []
            for r in rs:
                key = r['key']
                r2 = TPodcast.find_one({'key': key}, projection=fields)
                if not r2:
                    print('PODCAST NOT FOUND. key = %s' % (key))
                    continue
                del r2['_id']
                docs.append(r2)
            r2 = {'key': toplist_key,
                  'docs': docs}
            TTopList.replace_one({'key': toplist_key}, r2, upsert=True)
        g = gevent.spawn(f, country, genre)
        pool.add(g)
    for country in ITUNES_COUNTRY_CODE.values():
        if country.find('_') != -1:
            continue
        g = gevent.spawn(f, country, 0)
        pool.add(g)
    pool.join()
    print('UPDATE TOPLIST DONE.')


if __name__ == '__main__':
    setup()
    fill_itunes_weight()
    merge_weight()
    update_toplist()
