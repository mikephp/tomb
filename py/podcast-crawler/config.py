#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

DB_HOST = 'localhost'
DB_NAME = 'pdcast'
DB_USER = 'root'
DB_PASS = '123456'
CACHE_EXPIRE_DAYS = 365
FORCE_PARSE_LOOKUP = False
# FORCE_PARSE_FEED = False
FORCE_PARSE_FEED = True

try:
    from local_config import *
except:
    pass
