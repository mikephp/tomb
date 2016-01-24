#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import gevent
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool

from stockfighter import Stockfighter
import time

st = Stockfighter.start_level('sell_side')
ACCOUNT = st['account']
VENUE = st['venues'][0]
STOCK = st['tickers'][0]
ft = Stockfighter(VENUE, ACCOUNT)
