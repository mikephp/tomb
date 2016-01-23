#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from gevent import monkey; monkey.patch_socket()
import urllib2
import gevent
import gevent.pool
from scrapy.selector import Selector
import os
import config as CF
import redis
import json

url_format = 'http://www.proxylists.net/cn_%d_ext.html'
dir_prefix_format = 'data/proxies_html_%s'
local_format = 'data/proxies_html_%s/cn_%d_ext.html'
page_num = 10

def fetch_page(date, pid):
    dir_prefix = dir_prefix_format % date
    if not os.path.exists(dir_prefix):
        os.mkdir(dir_prefix)

    local = local_format % (date, pid)
    url = url_format % (pid)
    if os.path.exists(local):
        data = open(local).read()
    else:
        print '{} ....'.format(url)
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        text = f.read()
        print '{} done'.format(url)
        with open(local, 'w') as fh:
            fh.write(text)
        data = text
    return data

def fetch_pages(date):
    for i in range(page_num):
        fetch_page(date, i)

def parse_page(date, pid):
    local = local_format % (date, pid)
    data = open(local).read()
    s1 = Selector(text = data).xpath('//tr/td/text()').extract()
    s1 = filter(lambda x: not x in ('\r\n', '\r\n\r\n'), s1)[1:]
    s2 = Selector(text = data).xpath('//tr/td/script/text()').extract()
    records = []
    begin_skip = len("eval(unescape('")
    end_skip = len("'));")
    for i in range(10):
        ss = s2[i][begin_skip:-end_skip].split('%')[1:]
        chrs = map(lambda x: chr(int(x, 16)), ss)[23:-3]
        addr = ''.join(chrs)
        (port, type, cn, date) = s1[i*4:(i+1) * 4]
        if type in ('Transparent', 'Anonymous'):
            t = type[0]
            records.append((addr, int(port), t, cn, date))
    return records

def parse_pages(date):
    records = []
    for i in range(page_num):
        records2 = parse_page(date, i)
        records.extend(records2)
    return records

def put_proxies_to_redis(date, records):
    key = 'available_proxies_%s' % (date)
    db = redis.Redis(host = CF.REDIS_HOST, port = CF.REDIS_PORT,
                     db = CF.REDIS_DB)
    db.delete(key)
    records = map(lambda x: '{}:{}'.format(x[0], x[1]), records)
    db.sadd(key, *records)

def get_proxies_from_redis(date):
    key = 'available_proxies_%s' % (date)
    db = redis.Redis(host = CF.REDIS_HOST, port = CF.REDIS_PORT,
                     db = CF.REDIS_DB)
    proxies = list(db.smembers(key))
    return proxies


def test():
    date = '20150930'
    fetch_pages(date)
    records = parse_pages(date)
    put_proxies_to_redis(date, records)
    proxies = get_proxies_from_redis(date)
    print proxies

if __name__ == '__main__':
    test()
