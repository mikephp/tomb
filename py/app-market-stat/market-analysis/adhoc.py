#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import config as CF
import run_apps as RA
import android_parse_apps
from pymongo import MongoClient
from app_fact import AppFact

CLIENT = MongoClient(CF.MONGO_URL)
DB = CLIENT.market_analysis

def get_possible_umkeys(af):
    keys = set()
    for (i, market) in enumerate(af.markets):
        naf = AppFact()
        naf.type = 'android'
        naf.market = market
        naf.bundleId = af.bundleId
        naf.version = af.versions[i]
        naf.compose_key()
        naf2 = RA.get_apps_ads_cache_data(DB, naf)
        if naf2 is None: continue
        umkey = naf2.__dict__.get('umkey', '')
        if not umkey: continue
        keys.add(umkey)
    return keys

import os
def export(date):
    dir_prefix = 'report/%s/' % (date)
    if not os.path.exists(dir_prefix):
        os.makedirs(dir_prefix)
    table = DB['apps_run_%s' % date]
    afs = table.find({'type':'android'})
    res = []
    for af2 in afs:
        af = AppFact()
        af.from_mongo_doc(af2)
        ads = af.ads.split(';')
        if 'push.getui' in ads and 'push.bdpush' in ads:
            keys = get_possible_umkeys(af)
            res.append((af, keys))
    lines = []
    for r in res:
        (af, keys) = r
        lines.append('%d, %s, %s, %s\n' % (af.rank, af.bundleId, af.title, ' '.join(keys)))
    fname = os.path.join(dir_prefix, 'adhoc.csv')
    with open(fname, 'w') as fh:
        fh.writelines(lines)

if __name__ == '__main__':
    import sys
    date = sys.argv[1]
    export(date)
