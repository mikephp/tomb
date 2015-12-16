#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import urllib2

saved_dir = 'book/'
prefix = 'http://www.2cto.com/shouce/Pythonbbf/'

import os

dirs = [saved_dir] + map(lambda x: saved_dir + x, ['_static', '_sources', '_images'])
for dir in dirs:
    if not os.path.exists(dir):
        os.makedirs(dir)

def get_page(id):
    f = saved_dir + '/' + id
    if os.path.exists(f):
        with open(f) as fh:
            data = fh.read()
            return data
    fh = urllib2.urlopen(prefix + id)
    data = fh.read()
    with open(f, 'w') as fh:
        fh.write(data)
    return data

Q = ['index.html', 'intro_zh.html', 'intro.html', 'next.html', 'advice.html'] + \
    ['ex{}.html'.format(i) for i in range(0, 53)]
pos = 0
import re
re_static = re.compile(r'href="(_static/([^"]+))"')
re_images = re.compile(r'src="(_images/([^"]+))"')
re_sources = re.compile(r'href="(_sources/([^"]+))"')
res = [re_static, re_images, re_sources]

while pos < len(Q):
    q = Q[pos]
    pos += 1
    print 'get_page {}'.format(q)
    data = get_page(q)
    if not q.endswith('.html'): continue
    static_obj = re_static.search(data)
    for rex in res:
        p = 0
        while p < len(data):
            obj = rex.search(data[p:])
            if not obj: break
            p += obj.end() + 1
            link = obj.group(1)
            if not link in Q:
                print 'add link {}'.format(link)
                Q.append(link)
