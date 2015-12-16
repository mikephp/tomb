#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import config as CF
from app_fact import AppFact
import android_parse_apps
import ios_parse_apps
import pymongo
from pymongo import MongoClient

TEST = False

def init_new_run(date):
    ios_afs = ios_parse_apps.read_afs(date)
    android_afs = android_parse_apps.read_afs(date)

    if TEST:
        # 测试只选出部分应用
        ios_afs = filter(lambda x: x.rank < 5, ios_afs)
        android_afs = filter(lambda x: x.rank <= 100, android_afs)

    afs = ios_afs + android_afs
    print 'new_run: len(afs) = %d' % (len(afs))
    client = MongoClient(CF.MONGO_URL)
    # database 'market_analysis'
    db = client.market_analysis
    # table apps_run_20150930
    table = db['apps_run_%s' % date]
    table.drop()
    table.create_index('bundleId')
    docs = []
    for af in afs:
        doc = af.to_mongo_doc()
        docs.append(doc)
        if len(docs) == 1000:
            print 'insert 1000 docs...'
            table.insert_many(docs)
            docs = []
    if len(docs):
        print 'insert %d docs...' % (len(docs))
        table.insert_many(docs)
        docs = []
    client.close()
    return afs

def fetch_unprocessed_afs(date):
    client = MongoClient(CF.MONGO_URL)
    db = client.market_analysis
    table = db['apps_run_%s' % date]
    afs = []
    for x in table.find({'processed' : 0}):
        af = AppFact()
        af.from_mongo_doc(x)
        afs.append(af)
    print 'unprocesed: len(afs) = %d' % (len(afs))
    client.close()
    return afs

from bson.objectid import ObjectId
def mark_af_processed(db, date, oid, ads = 'OK'):
    table = db['apps_run_%s' % date]
    _oid = ObjectId(oid)
    table.update_one({'_id': ObjectId(_oid)},
                 {'$set': {'processed': 1,
                          'ads' : ads}})

def get_unprocessed_count(db, date):
    table = db['apps_run_%s' % date]
    return table.count({'processed': 0})

def create_apps_ads_cache_table():
    client = MongoClient(CF.MONGO_URL)
    db = client.market_analysis
    table = db['apps_ads_cache']
    table.create_index('key')
def get_apps_ads_cache_data(db, af):
    table = db['apps_ads_cache']
    doc = table.find_one({'key': af.key})
    if doc is None: return None
    naf = AppFact()
    naf.from_mongo_doc(doc)
    return naf
def set_apps_ads_cache_data(db, af):
    table = db['apps_ads_cache']
    table.replace_one({'key': af.key}, af.to_mongo_doc(),upsert = True)

def create_apps_ads_history():
    client = MongoClient(CF.MONGO_URL)
    db = client.market_analysis
    table = db['apps_ads_history']
    table.create_index([('key', pymongo.ASCENDING),
                        ('date', pymongo.DESCENDING)])
def get_apps_ads_by_date(db, t, bundleId, date):
    table = db['apps_ads_history']
    key = '%s-%s' % (t, bundleId)
    doc = table.find_one({'key' : key, 'date' : date})
    return doc
def drop_apps_ads_by_date(db, date):
    table = db['apps_ads_history']
    table.delete_many({'date': date})
# def insert_new_apps_ads(db, t, bundleId, date, ads, title):
#     table = db['apps_ads_history']
#     key = '%s-%s' % (t, bundleId)
#     table.update({'key': key,
#                   'date': date},
#                   {'bundleId': bundleId,
#                    'type': t,
#                    'key': key,
#                    'date': date,
#                    'ads': ads,
#                    'title': title},
#                    upsert = True)
def make_app_ads_doc(t, bundleId, date, ads, title):
    doc = {'date': date, 'title': title, 'ads': ads, 'type': t,
           'bundleId': bundleId}
    key = '%s-%s' % (t, bundleId)
    doc['key'] = key
    return doc

def insert_new_apps_ads(db, docs):
    table = db['apps_ads_history']
    table.insert_many(docs)

def create_apps_stat_history():
    client = MongoClient(CF.MONGO_URL)
    db = client.market_analysis
    table = db['apps_stat_history']
    table.create_index([('key', pymongo.ASCENDING), # category + '.' + sdk_name
                        ('date', pymongo.DESCENDING)])
def get_apps_stat_by_date(db, key, date):
    table = db['apps_stat_history']
    doc = table.find_one({'key': key, 'date': date})
    return doc
def insert_new_apps_stat(db, key, date, doc):
    table = db['apps_stat_history']
    doc2 = doc.copy()
    doc2['key'] = key
    doc2['date'] = date
    table.replace_one({'key': key, 'date': date}, doc2, upsert = True)

from redis_queue import RedisQueue
import json
def make_rq(date):
    name = 'apps_run_%s' % date
    rq = RedisQueue(name, host = CF.REDIS_HOST, port = CF.REDIS_PORT, db = CF.REDIS_DB)
    return rq

def push_afs_to_redis_queue(afs, date):
    rq = make_rq(date)
    rq.clear()
    for af in afs:
        js = {'id' : str(af._id),
            'type': af.type,
            'bundleId' : af.bundleId,
            'markets': af.markets,
            'versions': af.versions,
            'urls': af.urls,
            }
        s = json.dumps(js)
        rq.put(s)

def main():
    import sys
    argv = sys.argv
    cmd = argv[1]
    if cmd == 'create':
        create_apps_ads_cache_table()
        create_apps_ads_history()
        create_apps_stat_history()
        return
    date = argv[2]
    global TEST
    if cmd == 'newrun':
        afs = init_new_run(date)
        push_afs_to_redis_queue(afs, date)
    elif cmd == 'rerun':
        afs = fetch_unprocessed_afs(date)
        push_afs_to_redis_queue(afs, date)
    elif cmd == 'test':
        TEST = True
        afs = init_new_run(date)
        push_afs_to_redis_queue(afs, date)

if __name__ == '__main__':
    main()
