#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from util import *
import itunes

import gevent
from gevent.pool import Pool

FIRST_BATCH = ('us', 'br', 'de', 'kr', 'in', 'mx', 'ru',
               'gb', 'jp', 'fr', 'es', 'cn', 'nl', 'pt', 'se', 'it')

TWeight = DB['weight']
TWeightFirstBatch = DB['weight_first_batch']


def fill_itunes_weight(run_all):
    print('FILL ITUNES WEIGHT ...')
    weight_table = TWeight if run_all else TWeightFirstBatch
    weight_table.drop()
    weight_table.create_index('key')
    comb = itunes.make_comb()
    for (country, genre) in comb:
        def f(country, genre):
            print('FILL ITUNES WEIGHT. (%s, %d)' % (country, genre))
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
                r2 = weight_table.find_one({'key': feed_key})
                if not r2:
                    r2 = {'key': feed_key, 'url': url}
                r2[field] = (idx + 1)
                ops.append(ReplaceOne({'key': feed_key}, r2, upsert=True))
            if ops:
                weight_table.bulk_write(ops)
            else:
                print('FILL ITUNES WEIGHT. NO OPS. (%s, %d)' %
                      (country, genre))
        if not run_all and country not in FIRST_BATCH:
            continue
        f(country, genre)
    for country in ITUNES_COUNTRY_CODE.values():
        if country.find('_') != -1:
            continue
        if not run_all and country not in FIRST_BATCH:
            continue
        f(country, 0)
    print('FILL ITUNES WEIGHT DONE.')


def merge_weight(run_all):
    weight_table = TWeight if run_all else TWeightFirstBatch
    rs = weight_table.find({})
    pool = Pool(size=32)

    print('MERGE WEIGHT ...')

    def f(r):
        keys = r.keys()
        iw_keys = filter(lambda x: x.startswith('iw_'), keys)
        for k in iw_keys:
            fw_key = k[3:]
            r[fw_key] = r[k]
        weight_table.replace_one({'key': r['key']}, r)

    for r in rs:
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    print('MERGE WEIGHT DONE.')


def update_toplist(run_all):
    pool = Pool(size=4)
    weight_table = TWeight if run_all else TWeightFirstBatch
    print('UPDATE TOPLIST ...')
    comb = itunes.make_comb()
    fields = ('feedUrl', 'description', 'title',
              'author', 'cover', 'itunes_cover', 'itunes_id',
              'key', 'releaseDate', 'trackCount')
    ctx = {'not-found': 0}
    for (country, genre) in comb:
        def f(country, genre):
            print('UPDATE TOPLIST (%s, %d) ...' % (country, genre))
            sort_field = '%s_%s' % (country, genre)
            toplist_key = sort_field
            rs = weight_table.find({}, projection=('key', 'url', ), sort=[
                (sort_field, pymongo.DESCENDING)], limit=200)
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
            print('UPDATE TOPLIST (%s, %d) DONE' % (country, genre))
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
    parser.add_argument('--just-update-toplist', action='store_true')
    args = parser.parse_args()
    if not args.just_update_toplist:
        fill_itunes_weight(args.run_all)
        merge_weight(args.run_all)
    update_toplist(args.run_all)
