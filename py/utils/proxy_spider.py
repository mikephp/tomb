#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from gevent import monkey; monkey.patch_socket()
import urllib2
import gevent
import gevent.pool
from scrapy.selector import Selector

url_format = 'http://www.proxylists.net/cn_%d_ext.html'
pages = 10
import os

def fetch_page(pid):
    if not os.path.exists('html'):
        os.mkdir('html')

    local = 'html/cn_%d_ext.html' % pid
    if os.path.exists(local):
        data = open(local).read()
    else:
        print '#%d ....' % pid
        url = url_format % pid
        # headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        #             'Accept-Encoding': 'default',
        #             'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        #             'Cache-Control':'max-age=0',
        #             # 'Connection':'keep-alive',
        #             # 'Cookie':'__utmt=1; __utma=204065105.1178036461.1442803412.1443250026.1443256201.4; __utmb=204065105.4.10.1443256201; __utmc=204065105; __utmz=204065105.1442803412.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        #             # 'Host':'www.proxylists.net'
        #             # 'If-Modified-Since':'Sat, 26 Sep 2015 07:31:53 GMT'
        #             # If-None-Match:e42876548d8188de669de66839a2079f
        #             'Upgrade-Insecure-Requests':'1',
        #             'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'
        # }
        # if pid != 0: headers['Referer'] = url_format % (pid - 1)
        headers = {}
        req = urllib2.Request(url, headers = headers)
        f = urllib2.urlopen(req)
        text = f.read()
        print '#%d done' % pid
        with open(local, 'w') as fh:
            fh.write(text)
        data = text
    return data

def fetch_pages_con():
    pool = gevent.pool.Pool(16)
    gs = []
    for i in range(pages):
        g = gevent.spawn(fetch_page, i)
        gs.append(g)
        pool.add(g)
    pool.join()

def fetch_pages_seq():
    for i in range(pages):
        fetch_page(i)

def parse_page(pid):
    local = 'html/cn_%d_ext.html' % pid
    if not os.path.exists(local): return
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

def parse_pages():
    records = []
    for i in range(pages):
        records2 = parse_page(i)
        if records2 is None: continue
        records.extend(records2)
    return records

def output_parse_pages():
    records = parse_pages()
    for record in records:
        print record

def test():
    # fetch_pages_con()
    # fetch_pages_seq()
    records = parse_pages()
    for record in records:
        print record

if __name__ == '__main__':
    test()
