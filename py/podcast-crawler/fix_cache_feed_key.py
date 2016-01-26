#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from util import *
import hashlib

rs = TCache.find({'tag': 'feed'})
for r in rs:
    key = r['key']
    rid = r['_id']
    pid = int(key.split('_')[1])
    cr = TPlaylist.find_one({'pid': pid})
    if not cr:
        continue
    url = cr['feedUrl']
    sign = hashlib.sha1(url).hexdigest()
    TCache.update_one({'_id': rid}, {'$set': {'key': sign, 'url': url}})
