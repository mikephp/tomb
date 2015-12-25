#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import gevent
import web
import pymongo
import config as CF
import json

urls = ("/index/", 'index',
        "/detail/", 'detail',
        '/labels/', 'labels',
        '/pop/', 'popular',)

app = web.application(urls, globals())

def viewcount_in_string(v):
    s = ''
    while(v >= 1000):
        s = ',' + '%03d' % (v % 1000) + s
        v /= 1000
    s = str(v) + s
    return s

LANG_MAPPING_V1 = ('', 'en', 'fr', 'de', 'ja', 'pt', 'es', 'it', 'zh', 'ru',)
LANG_MAPPING_V2 = ('', 'en', 'ja', 'pt', 'zh', 'ru',)

class index:
    def GET(self):
        ctx = web.input(s = 0, sid = '', c = 20, lang = 0, v = 1, q = '')
        # print web.ctx.path, web.ctx.query
        s = int(ctx.s); sid = ctx.sid; c = int(ctx.c); lang_idx = int(ctx.lang); version = int(ctx.v); q = ctx.q
        # skip + limit
        # 性能不行再使用>sid & limit
        query = {}
        if version == 1:
            lang = '' if lang_idx > len(LANG_MAPPING_V1) else LANG_MAPPING_V1[lang_idx]
            if lang: query['lang'] = lang
        elif version == 2:
            lang = '' if lang_idx > len(LANG_MAPPING_V2) else LANG_MAPPING_V2[lang_idx]
            if lang == 'en': query['lang'] = {'$in': ['en', 'fr', 'de', 'es', 'it']}
            elif lang: query['lang'] = lang
        # print('query on mongo = %s' % query)
        projection_list = ['title', 'description', 'viewcount', 'thumb', 'key', '_id', 'bigthumbhd']
        sort_pred = [('viewcount', pymongo.DESCENDING)]
        if q:
            query['$text'] = {'$search': q}
            projection_dict = {}
            for x in projection_list: projection_dict[x] = True
            projection_dict['score'] = {'$meta': 'textScore'}
            sort_pred.insert(0, ('score', {'$meta': 'textScore'}))
        else:
            projection_dict = projection_list
        rs = CF.FACT_TABLE.find(query, skip = s, limit = c, projection = projection_dict, sort = sort_pred)
        vds = []
        for r in rs:
            vd = {}
            vd['tt'] = r['title']
            vd['desc'] = r['description']
            vd['views'] = viewcount_in_string(r['viewcount'])
            vd['im'] = r['thumb']
            vd['hdim'] = r['bigthumbhd']
            vd['id'] = r['key']
            vd['sid'] = str(r['_id'])
            vd['keys'] = r.keys()
            vds.append(vd)
        js = {'vds': vds,
              'version': version}
        web.header('Content-Type', 'application/json')
        return json.dumps(js)

class detail:
    def GET(self):
        ctx = web.input(id = '')
        vid = ctx.id
        r = CF.FACT_TABLE.find_one({'key': vid}, projection = ['videos'])
        ss = r['videos']
        vds = []
        for r in ss:
            vd = {}
            vd['id'] = r['key']
            vd['tt'] = r['title']
            vd['desc'] = r['description']
            vd['views'] = viewcount_in_string(r['viewcount'])
            vd['im'] = r['thumb']
            vd['hdim'] = r['bigthumbhd']
            vds.append(vd)
        js = {'vds': vds}
        web.header('Content-Type', 'application/json')
        return json.dumps(js)

class popular:
    def GET(self):
        js = {'terms': ['yoga with adriene', 'uchiha itachi', 'uchiha madara',
                        'best sex with yoga', 'free ponography']}
        web.header('Content-Type', 'application/json')
        return json.dumps(js)

wsgiapp = app.wsgifunc()
if __name__ == "__main__":
    app.run()
