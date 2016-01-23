#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import config as CF
import run_apps as RA
import android_parse_apps
from pymongo import MongoClient
from app_fact import AppFact

def get_android_afs(date, limit = None):
    afs = android_parse_apps.read_afs(date, limit)
    if limit: afs = afs[:limit]
    return afs

CLIENT = MongoClient(CF.MONGO_URL)
DB = CLIENT.market_analysis

def set_umps(afs):
    n = 0
    for af in afs:
        umps = []
        for (i, market) in enumerate(af.markets):
            naf = AppFact()
            naf.type = 'android'
            naf.market = market
            naf.bundleId = af.bundleId
            naf.version = af.versions[i]
            naf.compose_key()
            naf2 = RA.get_apps_ads_cache_data(DB, naf)
            if naf2 is None:
                n += 1
                umkey = ''
                umchl = ''
            else:
                # assert(naf2 is not None)
                umkey = naf2.__dict__.get('umkey', '')
                umchl = naf2.__dict__.get('umchl', '')
            umps.append((umkey, umchl))
        af.umps = umps
    print '%d items are None' % n

def test():
    date = '20151028'
    afs = get_android_afs(date, 100)
    set_umps(afs)
    for af in afs:
        if any(map(lambda x: x[0] or x[1], af.umps)):
            print af.bundleId, af.title, af.markets, af.umps

import os
def export(date, limit):
    dir_prefix = 'report/%s/' % (date)
    if not os.path.exists(dir_prefix):
        os.makedirs(dir_prefix)
    afs = get_android_afs(date, limit)
    set_umps(afs)
    lines = []
    for af in afs:
        if not any(map(lambda x: x[0] or x[1], af.umps)): continue
        for (i, market) in enumerate(af.markets):
            market = af.markets[i]
            version = af.versions[i]
            ump = af.umps[i]
            lines.append('%s,%s,%s,%s,%s,%s\n' % (
                af.bundleId, af.title, market, version,
                ump[0], ump[1]))
    fname = os.path.join(dir_prefix, 'android_top%d_channel.csv' % (limit))
    with open(fname, 'w') as fh:
        fh.writelines(lines)

if __name__ == '__main__':
    import sys
    date = sys.argv[1]
    export(date, 5000)
