#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import nova
import ngxtop.config_parser
import ngxtop.ngxtop
import gzip
import itertools
import urlparse
import datetime as dt
import traceback
import os

class Record(object):
    def __init__(self, data):
        self.data = data
        # self.query = self._parse_query()
        # self.castbox_ua = self._parse_castbox_ua()
        # self.remote_addr = self._parse_remote_addr()
        # self.request_time = self._parse_request_time()

    def __getattr__(self, name):
        _d = self.__dict__
        if name in ('query', 'castbox_ua', 'remote_addr', 'request_time'):
            f = '_parse_' + name
            if name not in _d:
                _d[name] = self.__class__.__dict__['_parse_' + name](self)
            return _d[name]
        return _d.get(name, None)

    def _parse_remote_addr(self):
        x = self.data['http_x_forwarded_for']
        if x and x != '-':
            # http://docs.aws.amazon.com/zh_cn/ElasticLoadBalancing/latest/DeveloperGuide/x-forwarded-headers.html
            # 代理转发出来的.
            return x.split(',')[0]
        return self.data['remote_addr']

    def _parse_request_time(self):
        s = self.data['time_local']
        try:
            x = dt.datetime.strptime(s[:-6], '%d/%b/%Y:%H:%M:%S')
            return x
        except:
            traceback.print_exc()
            return None

    def _parse_query(self):
        request = self.data['request']
        (_, p, _) = request.split(' ')
        ps = p.split('?', 1)
        query_string = ps[1] if len(ps) == 2 else ''
        query = urlparse.parse_qs(query_string)
        data = {k: v[0] for (k, v) in query.items()}
        return data

    def _parse_castbox_ua(self):
        p = self.data['http_x_castbox_ua']
        ps = filter(lambda x: x, p.split(';'))
        data = {}
        for p in ps:
            kv = p.split('=', 1)
            if len(kv) != 2: continue
            (k, v) = kv
            data[k] = v
        return data

class Parser(object):
    def __init__(self, log_format = nova.NGINX_LOG_FORMAT):
        self.log_format = log_format
        self.log_pattern = ngxtop.config_parser.build_pattern(log_format)

    def parse_file(self, f, fn = None):
        if fn: f = (x for x in f if fn(x))
        records = ngxtop.ngxtop.parse_log(f, self.log_pattern)
        return records

    def parse_files(self, files, fn = None):
        return itertools.chain(*map(lambda x: self.parse_file(x, fn), files))

    def records_by_paths(self, files, paths, min_bytes_send = -1):
        if isinstance(paths, str): paths = [paths]
        def fn(x):
            for p in paths:
                if x.find('GET %s?' %p) != -1 or \
                  x.find('POST %s?' %p) != -1:
                  return True
            return False

        records = self.parse_files(files, fn = fn)
        records = (x for x in records if x.get('request_path') in paths and \
                x.get('status') < 400 and \
                x.get('bytes_sent') > min_bytes_send)
        return records
