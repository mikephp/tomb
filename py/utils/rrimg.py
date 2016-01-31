#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import urllib2
import re
import os
import json
import string
import threading

class Robot:
    def __init__(self, baseUrl, pageNum, reObj, saved):
        self.baseUrl = baseUrl
        self.pageNum = pageNum
        self.reObj = reObj
        self.saved = saved

    def ExtractLinks(self, htmlPage, reObj):
        links = []
        offset = 0
        while True:
            m = reObj.search(htmlPage, offset)
            if m:
                links.append(m.group(0))
                offset = m.end() + 1
            else:
                break
        return links

    def getHTMLPage(self, url, retry = 3):
        while True:
            try:
                fd = urllib2.urlopen(url)
                html = fd.read()
                return html
            except e:
                retry -= 1
                if retry == 0:
                    return None

    def run(self):
        if (os.path.exists(self.saved)):
            fp = open(self.saved)
            cached = json.load(fp)
            fp.close()
        else:
            cached = {}

        lks = []
        for i in range(0, self.pageNum):
            url = self.baseUrl + '?curpage=%d'%(i)
            print 'visit url(%s) ...'%(url)
            htmlPage = self.getHTMLPage(url)
            links = self.ExtractLinks(htmlPage, self.reObj)
            print 'visit url(%s) done'%(url)
            lks.extend(links)

        for lk in lks:
            if not lk in cached:
                cached[lk] = 0

        fp = open(self.saved, 'w')
        json.dump(cached, fp)
        fp.close()
        return cached.keys()

    def run2(self, urls):
        assert(self.pageNum == 1)
        if os.path.exists(self.saved):
            fp = open(self.saved)
            cached = json.load(fp)
            fp.close()
        else:
            cached = {}

        def save():
            fp = open(self.saved, 'w')
            json.dump(cached, fp)
            fp.close()

        cnt = 0
        for url in urls:
            if (url in cached):
                print 'cached...'
                continue
            print 'visit url(%s) ...'%(url)
            htmlPage = self.getHTMLPage(url)
            links = self.ExtractLinks(htmlPage, self.reObj)
            if len(links) == 0 : continue
            lk = string.split(links[0], ':', maxsplit = 1)[1][1:-1]
            lk = lk.replace('\\','')
            print lk
            cached[url]=lk

            # incremental saved.
            cnt += 1
            if ((cnt % 10) == 0):
                save()
        save()
        return cached

    def download(self, threadNum = 10):
        fp = open(self.saved)
        js = json.load(fp)
        fp.close()

        item = len(js.keys())
        pool = []
        for i in range(0, threadNum):
            start = i * item / threadNum
            end = (i + 1) * item / threadNum
            if i == (threadNum - 1):
                end = item - 1
            pool.append(threading.Thread(target=wget_download,
                        args=(js, start, end)))
        for i in range(0, threadNum):
            pool[i].start()
        for i in range(0, threadNum):
            pool[i].join()

def wget_download(js, s, e):
    def fixUrl2FileName(url):
        if url.startswith('http://'):
            url = url[len('http://'):]
        url = url.replace('/','.')
        return url + '.jpg' # is that ok ?

    keys = js.keys()[s:e]
    for k in keys:
        fname = fixUrl2FileName(k)
        fname = 'images/%s'%(fname)
        if os.path.exists(fname):
            print 'cached...'
            continue
        url = js[k]
        cmd = "wget -O '%s' '%s'"%(fname, url)
        print cmd
        os.system(cmd)

def createAlbumRobot(accNo = '600261907', pages = 7):
    reObj = re.compile(r'/\d+/album/\d+')
    return Robot('http://page.renren.com/%s/album'%(accNo), pages, reObj, 'album.list')

def createPhotoRobot(album, pages = 10):
    reObj = re.compile(r'/\d+/photo/\d+')
    return Robot('http://page.renren.com' + album, pages, reObj, 'photo.list')

def createPhotoLink():
    fp = open('photo.list')
    js = json.load(fp)
    fp.close()
    urls = map(lambda x : 'http://page.renren.com%s'%(x), js.keys())

    reObj = re.compile(r'\"(largeurl|large)\":"[^"]+"')
    robot = Robot('', 1, reObj, 'photo.link')
    robot.run2(urls)

def downloadPhoto():
    robot = Robot('', '', '', 'photo.link')
    robot.download()

if __name__ == '__main__':
    _createPhotoList = True
    _createPhotoLink = True
    _downloadPhoto = True

    if _createPhotoList :
        # following action costs too much.
        # better just run once
        # download photo list.
        robot = createAlbumRobot()
        albums = robot.run()
        for album in albums:
            robot = createPhotoRobot(album)
            robot.run()

    if _createPhotoLink :
        createPhotoLink()

    if _downloadPhoto:
        downloadPhoto()
