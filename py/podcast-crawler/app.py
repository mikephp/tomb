#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from util import *

import json as json_lib
import logging.config
logging.config.dictConfig(LOGGING_CONFIG)

from flask import Flask
from flask import make_response
from flask import request as AppRequest

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


@app.route('/category', methods=['GET'])
def category():
    country = AppRequest.args.get('country', 'us')
    cache_key = 'category_%s' % (country)
    value = read_cache(cache_key)
    if not value:
        v = GENRES_MAPPING.get(country, {})
        value = json_lib.dumps(v)
        write_cache(cache_key, value)
    return make_response(value)


@app.route('/top', methods=['GET'])
def top():
    country = AppRequest.args.get('country', 'us')
    genre = int(AppRequest.args.get('genre', 0))
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
                if 'itunes_cover' in x:
                    if x['itunes_cover']:
                        x['cover'] = x['itunes_cover']
                    del x['itunes_cover']
            value = json_lib.dumps(js)
            write_cache(cache_key, value)
        else:
            js = []
    return make_response(json_lib.dumps(js[skip: skip + limit]))

if __name__ == '__main__':
    app.run('0.0.0.0', 8080)
