#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

MONGO_URL = 'mongodb://127.0.0.1:27017'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 1
REDIS_QUEUE_TIMEOUT = 10

NUM_GREENLETS_PER_WORKER = 4

IPA_REPO = 'data/ipa-repo'
APK_REPO = 'data/apk-repo'
MB = 1024 * 1024
IPA_MAX_FILE_SIZE = 256 * MB
APK_MAX_FILE_SIZE = 256 * MB
CURL_CONNECT_TIME = 20
CURL_MAX_TIME = 256

import os
import logging
logging.basicConfig(format = '[%(levelname)s]%(name)s@%(funcName)s: %(msg)s', level = logging.DEBUG)

ANDROID_INTERVAL = 25
ANDROID_PAGE_NUM = 100
ANDROID_APP_TOPN = 2000
ANDROID_GAME_TOPN = 1000
CLEAN_APK = True

try:
    from local_config import *
except ImportError:
    pass

def read_android_ads_feat_txt():
    with open('android.txt','r') as fh:
        lines = fh.readlines()
    kind = None
    ads_feat_mapping = {}
    kind_texts = {}
    sdk_text = None
    sdk_texts = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'): continue
        if line.startswith('>'):
            (_, sdk_text, url) = line.split(' ')
        elif line.startswith('====='):
            kind = line.split(' ')[1]
            text = line.split(' ')[2]
            ads_feat_mapping[kind] = {}
            kind_texts[kind] = text
        else:
            (sdk_name, path, url) = map(lambda x: x.strip(), line.split('|'))
            assert (sdk_text is not None)
            if sdk_text:
                sdk_texts[sdk_name] = sdk_text
                sdk_text = None
            if not path: raise Exception('path empty')
            ps = path.split(';')
            for p in ps:
                if p.startswith('/') or p.endswith('.class'):
                    raise Exception('invalid path = %d' % path)
            ps = map(lambda x: os.path.normpath(x), ps)
            ads_feat_mapping[kind][sdk_name] = ps
    return ads_feat_mapping, kind_texts, sdk_texts
(ANDROID_ADS_FEAT_MAPPING, ANDROID_KIND_TEXTS, ANDROID_SDK_TEXTS) = read_android_ads_feat_txt()

def read_ios_ads_feat_txt():
    # with open('ios_ads_feat.txt', 'r') as fh:
    with open('ios.txt', 'r') as fh:
        lines = fh.readlines()
    kind = None
    ads_feat_mapping = {}
    sdk_text = None
    sdk_texts = {}
    kind_texts = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'): continue
        if line.startswith('>'):
            (_, sdk_text) = line.split(' ')
        elif line.startswith('====='):
            kind = line.split(' ')[1]
            text = line.split(' ')[2]
            ads_feat_mapping[kind] = {}
            kind_texts[kind] = text
        else:
            (sdk_name, class_name) = map(lambda x: x.strip(), line.split('|'))
            assert (sdk_text is not None)
            sdk_texts[sdk_name] = sdk_text
            sdk_text = None
            ads_feat_mapping[kind][sdk_name] = class_name.split(';')
    return ads_feat_mapping, kind_texts, sdk_texts
(IOS_ADS_FEAT_MAPPING, IOS_KIND_TEXTS, IOS_SDK_TEXTS) = read_ios_ads_feat_txt()

TRANSFORM_DATA = (('weibo', 'social'),
                  ('tcweibo', 'social'),
                  ('qzone', 'social'),
                  ('weixin', 'social'),
                  ('BugHD', 'analysis'),
                  ('OneAPM', 'analysis'),
                  ('networkbench', 'analysis'),
                  ('Critterism', 'analysis'),
                  ('NewRelic', 'analysis'))
def transform_ads_feat_mapping(mapping):
    nm = {}
    for kind in mapping.keys():
        for sdk in mapping[kind].keys():
            data = mapping[kind][sdk]
            for p in TRANSFORM_DATA:
                if sdk == p[0]:
                    kind = p[1]
            if kind not in nm: nm[kind] = {}
            nm[kind][sdk] = data
    return nm
ANDROID_ADS_FEAT_MAPPING = transform_ads_feat_mapping(ANDROID_ADS_FEAT_MAPPING)
IOS_ADS_FEAT_MAPPING = transform_ads_feat_mapping(IOS_ADS_FEAT_MAPPING)

ANDROID_UMSDKS = ('umana', 'umsocial', 'umpush', 'umim')
IOS_UMSDKS = ('umana', 'umsocial', 'umpush')

import string
def transform_ads(ads):
    s = set()
    for ad in ads:
        (kind, sdk) = string.split(ad, '.', maxsplit = 1)
        for p in TRANSFORM_DATA:
            if sdk == p[0]:
                kind = p[1]
        s.add('%s.%s' % (kind, sdk))
    return list(s)

import time
def days_before(date, days):
    st = time.strptime(date, '%Y%m%d')
    s = time.mktime(st) - (days * 3600 * 24)
    st2 = time.localtime(int(s))
    return time.strftime('%Y%m%d', st2)

def months_before(date, months):
    st = time.strptime(date, '%Y%m%d')
    mon = st.tm_mon - months
    year = st.tm_year
    while mon <= 0:
        mon += 12
        year -= 1
    return '%04d%02d%02d' % (year, mon, st.tm_mday)

RUN_INTERVAL_DAYS = 7
REPORT_BACKTRACE_NUMBER = 11
SUBPROCESS_TIMEOUT = 120
