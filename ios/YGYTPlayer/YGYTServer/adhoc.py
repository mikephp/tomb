#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import util

def run(vid):
    data = util.video_info(vid)
    streams = data['streams']
    for s in streams[::-1]:
        if s['ext'] == 'mp4':
            data['stream'] = s
    fields = ('key', 'title', 'description', 'viewcount', 'thumb', 'bigthumb', 'bigthumbhd', 'length', 'stream')
    info = {}
    for f in fields:
        info[f] = data[f]
    return info

import json
vids = ('tLku-s20EBE', 'rGyD3SpiND0')
with open('output.json', 'w') as fh:
    rs = []
    for vid in vids:
        info = run(vid)
        rs.append(info)
    s = json.dumps(rs)
    fh.write(s)
