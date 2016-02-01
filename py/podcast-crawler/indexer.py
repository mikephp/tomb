#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from util import *
from gevent.pool import Pool
import feedparser
import dateutil.parser
import datetime as dt
import elasticsearch.helpers
import mmh3
import os

# https://www.elastic.co/guide/en/elasticsearch/reference/2.1/analysis-lang-analyzer.html
SUPPORT_LANGUAGES = {
    'en': 'english',
    'ja': 'kuromoji',
    'de': 'german',
    'fr': 'french',
    'es': 'spanish',
    'ko': 'cjk',
    'zh': 'smartcn',
    'sv': 'swedish',
    'ru': 'russian',
    'ar': 'arabic',
    'pt': 'portuguese',
    'pt-br': 'brazilian',
    'it': 'italian',
    'no': 'norwegian',
    'tr': 'turkish',
    'da': 'danish',
    'nl': 'dutch',
    'cs': 'czech',
    'fi': 'finnish',
    'hu': 'hungarian',
    'ca': 'catalan',
    'ro': 'romanian',
    'th': 'thai'
}


def create_es_index():
    for k in SUPPORT_LANGUAGES:
        v = SUPPORT_LANGUAGES[k]
        print('create es index. cc = %s, plugin = %s' % (k, v))
        ES.indices.create(index='pdindex-%s' % (k), ignore=400)
        ES.indices.put_mapping(doc_type='feed', body={
            "properties": {
                "title": {
                    "type": "string",
                    "analyzer": v
                },
                "description": {
                    "type": "string",
                    "analyzer": v
                },
                "track_title": {
                    "type": "string",
                    "analyzer": v
                },
                "track_description": {
                    "type": "string",
                    "analyzer": v
                },
                "author": {
                    "type": "string",
                    "analyzer": v
                },
                "genres": {
                    "type": "integer"
                },
                "country": {
                    "type": "string",
                    "index": "not_analyzed"
                }
            }
        }, index='pdindex-%s' % k)
        ES.indices.put_mapping(doc_type='track', body={
            "properties": {
                "title": {
                    "type": "string",
                    "analyzer": v
                },
                "description": {
                    "type": "string",
                    "analyzer": v
                },
                "author": {
                    "type": "string",
                    "analyzer": v
                },
                "genres": {
                    "type": "integer"
                },
                "country": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "url": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "feed_key": {
                    "type": "string",
                    "index": "not_analyzed"
                }
            }
        }, index='pdindex-%s' % k)


def format_language(lang):
    if not lang:
        return 'en'
    x = lang.lower().replace('_', '-')
    x = x[:5]
    if x in ('pt-br',):
        return x
    x = x[:2]
    if x in SUPPORT_LANGUAGES:
        return x
    return 'en'


def test_coverage():
    with open('lang_dist') as fh:
        d = json_lib.load(fh)
    d2 = [(u, v) for (u, v) in d.items()]
    d2.sort(lambda x, y: -cmp(x[1], y[1]))
    for (x, y) in d2:
        x2 = format_language(x)
        print('%10s -> %s' % (x, x2))


def put_feed_doc(ops, lang, key, doc):
    # print('PUT FEED DOC. lang = %s, key = %s' % (lang, key))
    # ES.index(index='pdindex-%s' % lang, doc_type='feed', body=doc, id=key)
    ops.append((lang, 'feed', key, doc))


def put_track_doc(ops, lang, key, doc):
    # print('PUT TRACK DOC. lang = %s, key = %s' % (lang, key))
    # ES.index(index='pdindex-%s' % lang, doc_type='track', body=doc, id=key)
    ops.append((lang, 'track', key, doc))


def put_docs(ops):
    if not ops:
        return
    rs = []
    for op in ops:
        (lang, type, key, doc) = op
        r = {'_op_type': 'index',
             '_index': 'pdindex-%s' % (lang),
             '_type': type,
             '_id': key,
             '_source': doc}
        if type == 'feed':
            print("PUT DOC. type = %s, lang = %s, key = %s" %
                  (type, lang, key))
        rs.append(r)
    ys = elasticsearch.helpers.streaming_bulk(ES, rs)
    # force evaluation.
    for y in ys:
        pass


def index_feed(force=False):
    pool = Pool(size=16)
    rs = TPodcast.find(INDEX_PIDS_QUERY, no_cursor_timeout=True)
    print('INDEX FEED ...')

    def f(r):
        url = r.feedUrl
        feed_key = get_feed_key(url)
        cr = TESBook.find_one({'key': feed_key})
        if not force and cr and cr['updateDate'] >= r.parsedDate:
            # print('INDEX FEED CACHED. FEED ON DATE')
            return
        cr2 = TCache.find_one({'key': feed_key})
        entries = []
        if not cr2.get('skip', 0) and 'value' in cr2:
            data = cr2['value']
            dom = feedparser.parse(cr2['value'])
            entries = dom.entries
        ops = []
        eops = []
        if not force and 'TRACK' in os.environ:
            for entry in entries:
                on_track(r, feed_key, entry, ops, eops)
        if not cr:
            cr = {'key': feed_key, 'sign': 0, 'tag': 'feed'}
        on_feed(r, feed_key, cr, eops, entries)
        put_docs(eops)
        cr['updateDate'] = r.parsedDate
        ops.append(ReplaceOne({'key': feed_key}, cr, upsert=True))
        TESBook.bulk_write(ops)

    def on_track(r, feed_key, entry, ops, eops):
        url = entry.get('id', '')
        track_key = get_feed_key(url)
        doc_key = feed_key[:8] + track_key
        cr = TESBook.find_one({'key': doc_key})
        doc = {}
        doc['title'] = entry.get('title', '').encode('utf-8')
        description = entry.get('summary', '') or entry.get('description', '')
        doc['description'] = description.encode('utf-8')
        doc['author'] = entry.get('author', '').encode('utf-8')
        doc['url'] = url
        doc['country'] = r.country
        doc['genres'] = r.genres
        doc['feed_key'] = feed_key
        if not cr:
            cr = {'key': doc_key, 'sign': 0, 'tag': 'track'}
        hs = doc['title'] + doc['description'] + doc['author']
        sign = mmh3.hash(hs)
        if not force and cr['sign'] == sign:
            print('INDEX FEED CACHED. TRACK ON SIGN')
            return False
        lang = format_language(getattr(r, 'language', ''))
        put_track_doc(eops, lang, doc_key, doc)
        cr['sign'] = sign
        ops.append(ReplaceOne({'key': doc_key}, cr, upsert=True))
        return True

    def on_feed(r, feed_key, cr, eops, entries):
        feed_doc = {}
        feed_doc['title'] = r.title
        feed_doc['description'] = r.description
        feed_doc['author'] = r.author
        feed_doc['country'] = r.country
        feed_doc['genres'] = r.genres
        tts = []
        tds = []
        for entry in entries:
            tts.append(entry.get('title', '').encode('utf-8'))
            description = entry.get(
                'summary', '') or entry.get('description', '')
            tds.append(description.encode('utf-8'))
        feed_doc['track_title'] = tts
        feed_doc['track_description'] = tds
        lang = format_language(getattr(r, 'language', ''))
        put_feed_doc(eops, lang, feed_key, feed_doc)

    for r in rs:
        if 'parsed' not in r:
            continue
        r = Document.from_json(r)
        pool.spawn(f, r)
    pool.join()

    print('INDEX FEED DONE.')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-coverage', action='store_true')
    parser.add_argument('--create-index', action='store_true')
    parser.add_argument('--do-index', action='store_true')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    if args.test_coverage:
        test_coverage()
    if args.create_index:
        create_es_index()
    if args.do_index:
        index_feed(args.force)
