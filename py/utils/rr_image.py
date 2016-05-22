#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import urllib2
import re
import os
import json
import string
import threading


import requests
from bs4 import BeautifulSoup
import hashlib

CACHE_DIR = 'cache/'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def get_url(url, ss = None):
    if not ss:
        ss = requests.session()
    key = hashlib.md5(url).hexdigest()
    cache = CACHE_DIR + key
    if os.path.exists(cache):
        data = open(cache).read()
        return data
    r = ss.get(url)
    with open(cache, 'w') as fh:
        fh.write(r.content)
    return r.content


def get_album_urls(station_id = 600261907):
    cache = CACHE_DIR + 'album.urls.txt'
    if not os.path.exists(cache):
        ss = requests.session()
        urls = []
        init_url = 'http://page.renren.com/%d/album' % station_id

        def f(url, init = False):
            print('get url %s' % url)
            data = get_url(url, ss)
            bs = BeautifulSoup(data)
            xs = bs.select('#tabBody > div > div > div > table > tbody > tr > td > div > a')
            for x in xs:
                path = x.attrs['href']
                urls.append('http://page.renren.com' + path)
            if init:
                xs = bs.select('#tabBody > div > div > div > ol > li > a')
                last_page = int(xs[-1].attrs['href'].split('=')[-1])
                return last_page

        last_page = f(init_url, True)
        for x in range(1, last_page + 1):
            url = init_url + '?curpage=%d' % x
            f(url)

        with open(cache, 'w') as fh:
            fh.writelines(map(lambda x: x + '\n', urls))
        return urls

    with open(cache) as fh:
        return [x.strip() for x in fh]


def get_image_urls(album_url):
    album_id = album_url.split('/')[-1]
    cache = CACHE_DIR + 'image.urls.%s.txt' % album_id
    if os.path.exists(cache):
        with open(cache) as fh:
            return [x.strip() for x in fh]

    curpage = 0
    ss = requests.session()
    images = []
    while True:
        url = album_url + '?curpage=%d' % curpage
        print('get url %s' % url)
        data = get_url(url, ss)
        bs = BeautifulSoup(data)
        xs = bs.select('#single-column > table > tbody > tr > td > a')
        for x in xs:
            images.append('http://page.renren.com' + x.attrs['href'])
        # 最后一页
        xs = bs.select('#content > div.pager-top > ol > li > a')
        if not xs or 'class' not in xs[-1].attrs:
            break
        curpage += 1

    with open(cache, 'w') as fh:
        fh.writelines(map(lambda x: x + '\n', images))
    return images

if __name__ == '__main__':
    urls = get_album_urls()
    imgs = []
    for url in urls:
        images = get_image_urls(url)
        imgs.extend(images)
    with open('rr_image.urls.txt', 'w') as fh:
        fh.writelines(map(lambda x: x + '\n', imgs))
