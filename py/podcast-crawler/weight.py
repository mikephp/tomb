#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from util import *
import itunes

import gevent
from gevent.pool import Pool

FIRST_BATCH = ('us', 'br', 'de', 'kr', 'in', 'mx', 'ru',
               'gb', 'jp', 'fr', 'es', 'cn', 'nl', 'pt', 'se', 'it')


def setup():
    TWeight.drop()


def fill_itunes_weight(run_all):
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
            ops = []
            for (idx, xpid) in enumerate(pids):
                (pid, title) = xpid
                r = TPlaylist.find_one({'pid': pid})
                if not r or 'feedUrl' not in r:
                    print('FILL ITUNES WEIGHT. NOT FOUND %d' % pid)
                    continue
                url = r['feedUrl']
                feed_key = get_feed_key(url)
                r2 = TWeight.find_one({'key': feed_key})
                if not r2:
                    r2 = {'key': feed_key, 'url': url}
                r2[field] = (idx + 1)
                ops.append(ReplaceOne({'key': feed_key}, r2, upsert=True))
            if ops:
                TWeight.bulk_write(ops)
            else:
                print('FILL ITUNES WEIGHT. NO OPS. (%s, %d)' %
                      (country, genre))
        if not run_all and country not in FIRST_BATCH:
            continue
        g = gevent.spawn(f, country, genre)
        pool.add(g)
    for country in ITUNES_COUNTRY_CODE.values():
        if country.find('_') != -1:
            continue
        if not run_all and country not in FIRST_BATCH:
            continue
        g = gevent.spawn(f, country, 0)
        pool.add(g)
    pool.join()
    print('FILL ITUNES WEIGHT DONE.')


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


def update_toplist(run_all):
    pool = Pool(size=4)
    print('UPDATE TOPLIST ...')
    comb = itunes.make_comb()
    fields = ('feedUrl', 'description', 'title',
              'author', 'cover', 'itunes_cover', 'trackCount',
              'releaseDate')
    ctx = {'not-found': 0}
    for (country, genre) in comb:
        def f(country, genre):
            sort_field = '%s_%s' % (country, genre)
            toplist_key = sort_field
            rs = TWeight.find({}, projection=('key', 'url', ), sort = [
                              (sort_field, pymongo.DESCENDING)], limit = 200)
            docs = []
            for r in rs:
                key = r['key']
                url = r['url']
                r2 = TPodcast.find_one({'key': key}, projection=fields)
                if not r2:
                    print('PODCAST NOT FOUND. key = %s url = %s' % (key, url))
                    ctx['not-found'] += 1
                    continue
                del r2['_id']
                docs.append(r2)
            r2 = {'key': toplist_key,
                  'docs': docs}
            TTopList.replace_one({'key': toplist_key}, r2, upsert=True)
        if not run_all and country not in FIRST_BATCH:
            continue
        g = gevent.spawn(f, country, genre)
        pool.add(g)
    for country in ITUNES_COUNTRY_CODE.values():
        if country.find('_') != -1:
            continue
        if not run_all and country not in FIRST_BATCH:
            continue
        g = gevent.spawn(f, country, 0)
        pool.add(g)
    pool.join()
    print('UPDATE TOPLIST NOT FOUND %d' % (ctx['not-found']))
    print('UPDATE TOPLIST DONE.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-all', action='store_true')
    args = parser.parse_args()
    setup()
    fill_itunes_weight(args.run_all)
    merge_weight()
    update_toplist(args.run_all)
