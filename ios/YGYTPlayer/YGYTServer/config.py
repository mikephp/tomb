#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

MONGO_URL = 'mongodb://127.0.0.1:27017'
EXPIRE_INTERVAL = 3600 * 24 * 365
YOUTUBE_API_KEY = 'AIzaSyAxJCBgslg3f4sZ2_UAxdiQtpUoiqLrlas'
# from gevent import monkey; monkey.patch_socket()

import pymongo
CLIENT = pymongo.MongoClient(MONGO_URL)
DB = CLIENT.ygyt
PLAYLIST_TABLE = DB.playlist
VIDEO_TABLE = DB.video
FACT_TABLE = DB.fact

BANNED_VIDEO_IDS = ('')
