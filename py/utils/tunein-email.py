#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import pymongo
import snappy
import requests
from bs4 import BeautifulSoup
import hashlib
import bson

client = pymongo.MongoClient()
cache_table = client.test.cache_table

urls = """USA	http://tunein.com/radio/United-States-r100436/""".split('\n')

urls = map(lambda x: map(lambda y: y.strip(), x.split("\t")), urls)

def get_sha1_key(s):
    return hashlib.sha1(s).hexdigest()

def _get(url):
    key = get_sha1_key(url)
    r = cache_table.find_one({'_id': key})
    if not r:
        # print('[request] url = %s' % url)
        r = requests.get(url)
        content = r.content
        data = bson.binary.Binary(snappy.compress(content))
        cache_table.insert_one({'_id': key, 'data': data})
    else:
        # print('[cached] url = %s' % url)
        data = r['data']
    content = snappy.decompress(data)
    return content

def get_regions(url):
    ct = _get(url)
    bs = BeautifulSoup(ct)
    xs = bs.select('#mainContent > div > div.group.clearfix.linkmatrix > ul > li > a')
    links = map(lambda x: 'http://tunein.com' + x.attrs['href'], xs)
    return links

def get_stations(url):
    ct = _get(url)
    bs = BeautifulSoup(ct)
    xs = bs.select('#mainContent > div > div > ul > li > a')
    links = map(lambda x: 'http://tunein.com' + x.attrs['href'], xs)
    return links

import re
EMAIL_REGEX = re.compile(r'mailto:([^"]+)')
def get_email(url):
    ct = _get(url)
    m = EMAIL_REGEX.search(ct)
    if m: return m.groups()[0]
    return None

import json
import os

def main():
    d = {}
    if os.path.exists('tunein-email.ckpt'):
        with open('tunein-email.ckpt') as fh:
            d = json.load(fh)
    cid = -1
    call = len(urls)
    for (country, url) in urls:
        cid += 1
        if country in d: continue
        emails = set()
        regions = get_regions(url)
        print('country = %s[%d/%d], regions = %d' % (country, cid, call, len(regions)))
        rall = len(regions)
        for (rid, region) in enumerate(regions):
            stations = get_stations(region)
            print('country = %s[%d/%d], region = %s[%d/%d], stations = %d' % (
                country, cid, call, region, rid, rall, len(stations)))
            for st in stations:
                email = get_email(st)
                if not email: continue
                emails.add(email)
        d[country] = list(emails)
        print('country = %s, emails = %d' % (country, len(emails)))
        with open('tunein-email.ckpt', 'w') as fh:
            json.dump(d, fh)

    with open('tunein-email.txt', 'w') as fh:
        for key in d:
            emails = d[key]
            lines = list(emails)
            lines.insert(0, '>>>>> country (%s) <<<<<' % key)
            fh.writelines(map(lambda x: x + '\n', lines))

if __name__ == '__main__':
    main()
