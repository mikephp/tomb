#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from gevent import monkey; monkey.patch_socket()
import gevent
import gevent.pool
from gevent.subprocess import Popen
import subprocess
import config as CF
from redis_queue import RedisQueue
import run_apps as RA
from pymongo import MongoClient
import json
import sys
# import feed_proxies as FP
import random
import traceback
import os
import urllib2
import socket
import time
import logging
import ads_feat_detector as AFD
from app_fact import AppFact

LOG = None
IOS_DETECTOR = None
ANDROID_DETECTOR = None

def work(date, gid):
    client = MongoClient(CF.MONGO_URL)
    db = client.market_analysis
    rq = RA.make_rq(date)
    # _proxies = FP.get_proxies_from_redis(date)
    _proxies = []
    unique_id = '%s.%d.%d' % (socket.gethostname(), os.getpid(), gid)
    LOG.info('worker unique id = %s' % (unique_id))

    random.seed(unique_id)
    def loop():
        item = rq.get(block = True, timeout = CF.REDIS_QUEUE_TIMEOUT)
        if not item:
            if rq.qsize() == 0: return False
            else: True
        js = json.loads(item)
        oid = js['id']
        class Context:
            date = date
            proxies = _proxies
            type = js['type']
            bundleId = js['bundleId']
            markets = js['markets']
            versions = js['versions']
            urls = js['urls']
            database = db
        ctx = Context()
        # 没有任何下载市场.
        if not ctx.markets:
            ctx.ads = 'ENOSRC'
            RA.mark_af_processed(db ,date, oid, ctx.ads)
            return True

        ctxs = decompose_ctx(ctx)
        ctx.ads = actual_work2(ctxs)
        LOG.info('mark %s(%s) processed' % (ctx.type, ctx.bundleId))
        RA.mark_af_processed(db, date, oid, ctx.ads)
        for ctx in ctxs:
            # remove apk file.
            (f, ft) = binary_file_pairs(ctx)
            if os.path.exists(f) and CF.CLEAN_APK:
                os.remove(f)
        return True
    while True:
        try:
            if not loop(): break
        except Exception as e:
            LOG.exception(e)
            LOG.error(traceback.format_exc())
    return 'OK'

def decompose_ctx(ctx2):
    ctxs = []
    for idx in range(len(ctx2.markets)):
        class Context:
            date = ctx2.date
            proxies = ctx2.proxies
            type = ctx2.type
            database = ctx2.database
            bundleId = ctx2.bundleId
            market = ctx2.markets[idx]
            version = ctx2.versions[idx]
            url = ctx2.urls[idx]
        ctx = Context()
        ctxs.append(ctx)
    return ctxs

def actual_work(ctx):
    af = AppFact()
    af.type = ctx.type
    af.market = ctx.market
    af.bundleId = ctx.bundleId
    af.version = ctx.version
    af.compose_key()
    def get_names():
        naf = RA.get_apps_ads_cache_data(ctx.database, af)
        if naf is not None:
            zs = naf.ads
            names = AFD.decompress_names(zs)
            return names
        f = try_download(ctx)
        if f.startswith('E'):
            names = f
        elif ctx.type == 'ios':
            names = IOS_DETECTOR.try_decode_ipa(f)
        elif ctx.type == 'android':
            (names, ump) = ANDROID_DETECTOR.try_decode_apk(f)
            af.umkey = ump[0]
            af.umchl = ump[1]
        zs = AFD.compress_names(names)
        af.ads = zs
        RA.set_apps_ads_cache_data(ctx.database, af)
        return names
    names = get_names()
    if isinstance(names, str):
        ctx.ads = names
    else:
        ads = AFD.find_ads(names, ctx.type)
        ctx.ads = ';'.join(ads)
    return 0

def actual_work2(ctxs):
    ads = set()
    for ctx in ctxs:
        LOG.debug('process %s(%s-%s @ %s) ....' % (ctx.type, ctx.bundleId, ctx.version, ctx.market))
        actual_work(ctx)
        LOG.debug('process %s(%s-%s @ %s) DONE' % (ctx.type, ctx.bundleId, ctx.version, ctx.market))
        ads0 = ctx.ads.split(';')
        for ad in ads0: ads.add(ad)
    return ';'.join(list(ads))

def binary_file_pairs(ctx):
    if ctx.type == 'ios':
        f = '%s/%s-%s.ipa' % (CF.IPA_REPO, ctx.bundleId, ctx.version)
        ft = '%s/%s-%s.ipa.part' % (CF.IPA_REPO, ctx.bundleId, ctx.version)
    elif ctx.type == 'android':
        f = '%s/%s-%s-%s.apk' % (CF.APK_REPO, ctx.market, ctx.bundleId, ctx.version)
        ft = '%s/%s-%s-%s.apk.part' % (CF.APK_REPO, ctx.market, ctx.bundleId, ctx.version)
    return (f, ft)

def try_download(ctx, retries = 5):
    (f, ft) = binary_file_pairs(ctx)
    if os.path.exists(f): return f
    non_proxy_retries = 2 # 不使用proxy尝试次数.
    while True:
        args = ['curl', '-A', 'PPHelperNS/2.2.4 CFNetwork/711.1.16 Darwin/14.0.0', '-L', '-C', '-']
        if not non_proxy_retries and ctx.proxies:
            proxy_id = random.randint(0, len(ctx.proxies) - 1)
            proxy = ctx.proxies[proxy_id]
            args.extend(['--proxy', proxy])
        else:
            non_proxy_retries -= 1

        args.extend(['--connect-time', CF.CURL_CONNECT_TIME])
        args.extend(['--max-time', CF.CURL_MAX_TIME])
        args.extend(['--max-filesize', CF.IPA_MAX_FILE_SIZE if ctx.type == 'ios' else CF.APK_MAX_FILE_SIZE])
        args.extend([ '-o', ft, ctx.url])
        LOG.debug('args = %s' % args)
        args = map(lambda x: str(x), args)
        cmd = ' '.join(args)
        p = Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        code = p.wait()
        (out,err) = p.communicate()
        if code != 0:
            if code == 63: # file size exceeds
                return 'EF2BIG'
            LOG.warning('download %s, error log = %s' % (f, err))
            retries -= 1
            if retries == 0: break
            else: continue
        else:
            if os.path.exists(ft):
                LOG.info('file %s downloaded OK' % f)
                os.rename(ft, f)
                return f
            return 'EDOWNLOAD'
    return 'EDOWNLOAD'

def main(date):
    pool = gevent.pool.Pool(CF.NUM_GREENLETS_PER_WORKER)
    global LOG, IOS_DETECTOR, ANDROID_DETECTOR
    LOG = logging.getLogger('queue_worker')
    LOG.setLevel(logging.DEBUG)
    handler = logging.FileHandler('queue_worker.log')
    handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s]%(name)s@%(funcName)s: %(msg)s'))
    LOG.addHandler(handler)
    IOS_DETECTOR = AFD.IOSAdsFeatureDetector(LOG)
    ANDROID_DETECTOR = AFD.AndroidAdsFeatureDetector(LOG)
    for i in range(CF.NUM_GREENLETS_PER_WORKER):
        g = gevent.spawn(work, date, i)
        pool.add(g)
    pool.join()

if __name__ == '__main__':
    date = sys.argv[1]
    main(date)
