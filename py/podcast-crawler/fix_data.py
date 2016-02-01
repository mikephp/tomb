#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from util import *


def fix_playlist_dup_pid():
    rs = TPlaylist.find({}, projection=('pid', ))
    print('FIX PLAYLIST ...')
    for r in rs:
        pid = r['pid']
        rs2 = [u for u in TPlaylist.find({'pid': pid})]
        if len(rs2) == 1:
            continue
        print('FIX PID (%d)' % (pid))
        nr = {}
        country = []
        genres = []
        for r2 in rs2:
            nr.update(r2)
            for x in r2['country']:
                if x not in country:
                    country.append(x)
            for x in r2['genres']:
                if x not in genres:
                    genres.append(x)
        del nr['_id']
        nr['country'] = country
        nr['genres'] = genres
        ops = []
        ops.append(InsertOne(nr))
        for r2 in rs2:
            ops.append(DeleteOne({'_id': r2['_id']}))
        TPlaylist.bulk_write(ops)
    print('FIX PLAYLIST DONE.')


def fix_playlist_clear_skip():
    TPlaylist.update_many({'skip': 1}, {'$unset': {'skip': 1, 'comment': 1}})


def fix_cache_feed_clear_skip():
    TCache.update_many({'tag': 'feed', 'skip': 1}, {
                       '$unset': {'skip': 1, 'comment': 1}})

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--fix-playlist-dup-pid', action='store_true')
    parser.add_argument('--fix-playlist-clear-skip', action='store_true')
    parser.add_argument('--fix-cache-feed-clear-skip', action='store_true')
    args = parser.parse_args()
    if args.fix_playlist_dup_pid:
        fix_playlist_dup_pid()
    if args.fix_playlist_clear_skip:
        fix_playlist_clear_skip()
    if args.fix_cache_feed_clear_skip:
        fix_cache_feed_clear_skip()
