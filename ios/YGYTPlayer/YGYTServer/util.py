#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import config as CF
import string
import pprint
import urllib2
import traceback
import os
import re
import pafy
pafy.set_api_key(CF.YOUTUBE_API_KEY)
import gevent
# gevent.queue
import urlparse


def parse_videos_csv(fname='videos.tsv'):
    with open(fname) as fh:
        lines = map(lambda x: x.strip(), fh.readlines())
        fields = lines[0].split('\t')
        records = []
        for line in lines[1:]:
            if line.startswith('#'):
                continue
            item = line.split('\t')
            record = {}
            lessons = []
            labels = []
            record['lessons'] = lessons
            record['labels'] = labels
            for (i, v) in enumerate(item):
                key = fields[i]
                if not v:
                    continue
                if key.startswith('Label'):
                    labels.append(v)
                elif key.startswith('Lesson'):
                    lessons.append(v)
                else:
                    def format_key(key):
                        if key == 'Title':
                            return 'title'
                        elif key == 'Author':
                            return 'author'
                        elif key == 'Playlist':
                            return 'playlist'
                        elif key == 'Language':
                            return 'lang'
                        else:
                            return key
                    key2 = format_key(key)
                    record[key2] = v
            if 'playlist' in record:
                res = urlparse.urlparse(record['playlist'])
                qs = res.query.split('&')
                for q in qs:
                    if q.startswith('v') and not 'cover-id' in record:
                        record['cover-id'] = q[2:]
                    elif q.startswith('list='):
                        record[
                            'playlist'] = 'https://www.youtube.com/playlist?%s' % (q)
            record['title'] = '%s - %s' % (record['title'], record['author'])
            assert('cover-id' in record)
            record['key'] = record['cover-id']
            record['description'] = ''
            records.append(record)
        return records

import time


def mongo_cache_func(table, key, f, arg):
    data = table.find_one({'key': key})
    # print 'key = %s, data = %s' % (key, data)
    if data and data['_expire'] > time.time():
        print 'key (%s) cached.' % (key)
        return data
    data = f(arg)
    data['_expire'] = time.time() + CF.EXPIRE_INTERVAL
    table.replace_one({'key': key}, data, upsert=True)
    return data

import pafy


def nc_video_info(video_id):
    print '  > process video(%s)' % (video_id)
    v = pafy.new(video_id)
    data = {}
    data['key'] = v.videoid
    data['title'] = v.title
    data['description'] = v.description
    data['viewcount'] = v.viewcount
    data['thumb'] = v.thumb
    data['bigthumb'] = v.bigthumb
    data['bigthumbhd'] = v.bigthumbhd
    data['keywords'] = v.keywords
    data['length'] = v.length
    streams = []
    for s in v.streams:
        info = {}
        info['w'] = s.dimensions[0]
        info['h'] = s.dimensions[1]
        info['url'] = s.url
        info['url_https'] = s.url_https
        info['ext'] = s.extension
        streams.append(info)
    data['streams'] = streams
    return data


def video_info(video_id):
    return mongo_cache_func(CF.VIDEO_TABLE, video_id, nc_video_info, video_id)


def nc_playlist_info(playlist_id):
    print '  > process playlist(%s)' % (playlist_id)
    pl = pafy.get_playlist(playlist_id)
    data = {}
    data['key'] = playlist_id
    data['description'] = pl['description']
    data['items'] = map(lambda x: x['pafy'].videoid, pl['items'])
    return data


def playlist_info(playlist_id):
    return mongo_cache_func(CF.VIDEO_TABLE, playlist_id, nc_playlist_info, playlist_id)


def process_record(record):
    print '> process record(%s)' % (record['cover-id'])
    if 'playlist' in record:
        pi = playlist_info(record['playlist'])
        record['description'] = pi['description']
        record['lessons'] = pi['items']
    vi = video_info(record['cover-id'])
    for x in ('thumb', 'bigthumb', 'bigthumbhd'):
        record[x] = vi[x]
    vs = []
    for vid in record['lessons']:
        if vid in CF.BANNED_VIDEO_IDS:
            continue
        try:
            vi = video_info(vid)
        except:
            continue
        vs.append(vi)
        if not record['description']:
            record['description'] = vi['description']
    keywords = set()
    viewcount = 0
    for vi in vs:
        for k in vi['keywords']:
            keywords.add(k)
        viewcount += vi['viewcount']
    record['keywords_text'] = ' '.join(keywords)
    record['labels_text'] = ' '.join(record['labels'])
    record['viewcount'] = viewcount
    # videos
    nvs = []
    for vi in vs:
        nvi = {}
        for t in ('title', 'description', 'viewcount', 'thumb', 'bigthumb', 'bigthumbhd', 'key'):
            nvi[t] = vi[t]
        nvs.append(nvi)
    record['videos'] = nvs
    return record


def create_tables():
    CF.PLAYLIST_TABLE.create_index('key')
    CF.VIDEO_TABLE.create_index('key')
    CF.FACT_TABLE.create_index('key')
    CF.FACT_TABLE.create_index('lang')
    # CF.FACT_TABLE.create_index({'title':'text',
    #                             'labels_text': 'text',
    #                             'keywords_text': 'text'},
    #                             {'default_language': 'english'},
    #                             {'language_override': 'lang' })
"""
db.fact.dropIndex('text_index')
db.fact.createIndex({title:'text',labels_text:'text',keywords_text:'text'}, {weights: {title:10, labels_text:8, keywords_text:5}, name:'text_index'}, {'default_language':'english', 'language_override':'lang'})
"""


def do():
    create_tables()
    records = parse_videos_csv()
    for record in records:
        data = process_record(record)
        CF.FACT_TABLE.replace_one({'key': data['key']}, data, upsert=True)


def test():
    records = parse_videos_csv()
    pprint.pprint(records)

if __name__ == '__main__':
    do()
    # test()
