#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from util import *
from indexer import *

import json as json_lib
import logging.config
logging.config.dictConfig(LOGGING_CONFIG)

from flask import Flask
from flask import make_response
from flask import request as AppRequest

import requests

app = Flask(__name__)

app.debug = WEB_DEBUG


def read_cache(key):
    if app.debug:
        return
    try:
        value = RedisClient.get(key)
        if value:
            app.logger.debug('redis cached key: %s' % (key))
        return value
    except:
        app.logger.exception('redis failed')


def write_cache(key, value, timeout=3600):
    if app.debug:
        return
    try:
        RedisClient.setex(key, timeout, value)
    except:
        app.logger.exception('redis failed')


def format_country(c):
    if c not in GENRES_MAPPING:
        c = 'us'
    return c


def format_language(lang):
    if lang in SUPPORT_LANGUAGES:
        return lang
    if lang[:2] in SUPPORT_LANGUAGES:
        return lang[:2]
    return 'en'


def format_genre(g):
    if g not in ITUNES_PODCAST_ALL_GENRE_CODE.values():
        g = 0
    return g


@app.route('/genre', methods=['GET'])
def genre():
    country = AppRequest.args.get('country', 'us')
    country = format_country(country)
    kv = GENRES_MAPPING.get(country)
    v = [{'id': gid, 'name': name} for (gid, name) in kv.items()]
    res = {'code': 0, 'msg': 'OK', 'data': v}
    return make_response(json_lib.dumps(res), 200, {'Content-Type': 'application/json'})


def format_podcast(x):
    if 'cover' in x:
        x['cover-sm'] = x['cover']
        x['cover-me'] = x['cover']
        x['cover-bg'] = x['cover']
        del x['cover']
    if 'itunes_cover' in x:
        if x['itunes_cover']:
            x['cover-sm'] = x['itunes_cover']
            x['cover-me'] = x['itunes_cover'].replace(
                '30x30', '100x100')
            x['cover-bg'] = x['itunes_cover'].replace(
                '30x30', '600x600')
        del x['itunes_cover']


@app.route('/top', methods=['GET'])
def top():
    country = AppRequest.args.get('country', 'us')
    genre = int(AppRequest.args.get('genre', 0))
    country = format_country(country)
    genre = format_genre(genre)
    skip = int(AppRequest.args.get('skip', 0))
    limit = int(AppRequest.args.get('limit', 20))
    cache_key = 'top_%s_%d' % (country, genre)
    value = read_cache(cache_key)
    if value:
        js = json_lib.loads(value)
    else:
        query_key = '%s_%d' % (country, genre)
        r = TTopList.find_one({'key': query_key})
        if r:
            js = r['docs']
            for x in js:
                format_podcast(x)
        else:
            js = []
        value = json_lib.dumps(js)
        write_cache(cache_key, value)
    res = {'code': 0, 'msg': 'OK', 'data': js[skip: skip + limit]}
    return make_response(json_lib.dumps(res), 200, {'Content-Type': 'application/json'})


def make_search_payload(search_type, qs, country, genre):
    query = ''
    if qs:
        query += ' +(%s)' % (qs)
    if country:
        query += ' +country:(%s)' % (country)
    if genre:
        query += ' +genres:(%d)' % (genre)
    return_fields = []
    search_fields = ['title^5', 'author^3',
                     'description', 'track_title^2', 'track_description']
    payload = {
        'from': 0,
        'size': 100,
        'fields': return_fields,
        'query': {
            'query_string': {
                'fields': search_fields,
                'query': query,
                'use_dis_max': False
            }
        }
    }
    data = json_lib.dumps(payload)
    return data


def format_search_result(search_type, js):
    hits = js['hits']['hits']
    keys = map(lambda x: x['_id'], hits)
    fields = ('feedUrl', 'description', 'title',
              'author', 'cover', 'itunes_cover', 'itunes_id',
              'key', 'releaseDate', 'trackCount')
    # build index.
    mrs = TPodcast.find({'key': {'$in': keys}}, projection=fields)
    d = {}
    for r in mrs:
        d[r['key']] = r
    # back fill
    rs = []
    for k in keys:
        r = d[k]
        del r['_id']
        format_podcast(r)
        rs.append(r)
    return rs


@app.route('/search', methods=['GET'])
def search():
    country = AppRequest.args.get('country', 'us')
    language = AppRequest.args.get('language', 'en')
    genre = int(AppRequest.args.get('genre', 0))
    skip = int(AppRequest.args.get('skip', 0))
    limit = int(AppRequest.args.get('limit', 20))
    qs = AppRequest.args.get('q', '')
    search_type = 'feed'
    country = format_country(country)
    language = format_language(language)
    cache_key = 's_%s_%d_%s_%s' % (country, genre, language, qs)
    value = read_cache(cache_key)
    if value:
        js = json_lib.loads(value)
    else:
        url = ES_URL + 'pdindex-%s/feed/_search' % (language)
        data = make_search_payload(search_type, qs, country, genre)
        r = requests.post(url, data=data)
        js = format_search_result(search_type, r.json())
        value = json_lib.dumps(js)
        write_cache(cache_key, value)
    res = {'code': 0, 'msg': 'OK', 'data': js[skip:skip + limit]}
    return make_response(json_lib.dumps(res), 200, {'Content-Type': 'application/json'})


def format_search_itunes_result(js):
    rs = js['results']
    nrs = []
    pids = []
    for r in rs:
        nr = {}
        pid = r.get('collectionId', '')
        pids.append(pid)
        nr['itunes_id'] = pid
        nr['title'] = r.get('collectionName', '')
        nr['author'] = r.get('artistName', '')
        nr['description'] = ''
        nr['trackCount'] = r.get('trackCount', 0)
        nr['releaseDate'] = r.get('releaseDate', '')
        nr['cover-sm'] = r.get('artworkUrl30', '')
        nr['cover-me'] = r.get('artworkUrl100', '')
        nr['cover-bg'] = r.get('artworkUrl600', '')
        nrs.append(nr)
    # build index.
    mrs = TPodcast.find(
        {'itunes_id': {'$in': pids}}, projection=('itunes_id', 'description', 'key'))
    d = {}
    for r in mrs:
        if 'itunes_id' in r:
            d[r['itunes_id']] = r
    # back fill.
    for r in nrs:
        pid = r['itunes_id']
        mr = d.get(pid, None)
        if not mr:
            continue
        r['description'] = mr.get('description', '')
        r['key'] = mr.get('key', '')
    return nrs


@app.route('/search-itunes', methods=['GET'])
def search_itunes():
    country = AppRequest.args.get('country', 'us')
    language = AppRequest.args.get('language', 'en')
    skip = int(AppRequest.args.get('skip', 0))
    limit = int(AppRequest.args.get('limit', 20))
    qs = AppRequest.args.get('q', '')
    cache_key = 'si_%s_%s_%s' % (country, language, qs)
    value = read_cache(cache_key)
    if value:
        js = json_lib.loads(value)
    else:
        url = 'https://itunes.apple.com/search?media=podcast&term=%s&limit=200' % (
            qs)
        other = '&attribute=titleTerm&descriptionTerm&keywordsTerm&genreIndex&language=%s&country=%s' % (
            language, country)
        url += other
        if not USE_HTTPS:
            url = url.replace('https://', 'http://')
        r = requests.get(url)
        js = format_search_itunes_result(r.json())
        value = json_lib.dumps(js)
        write_cache(cache_key, value, 300)
    res = {'code': 0, 'msg': 'OK', 'data': js[skip:skip + limit]}
    return make_response(json_lib.dumps(res), 200, {'Content-Type': 'application/json'})

if __name__ == '__main__':
    app.run('0.0.0.0', 8080)
