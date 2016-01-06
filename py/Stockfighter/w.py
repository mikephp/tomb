#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from stockfighter import Stockfighter
import time

st = Stockfighter.start_level('chock_a_block')
ACCOUNT = st['account']
VENUE = st['venues'][0]
STOCK = st['tickers'][0]
ft = Stockfighter(VENUE, ACCOUNT)


while True:
    quote = ft.quote(STOCK)
    if not ('bid' in quote and 'ask' in quote and 'last' in quote):
        continue
    print('bid: %d(+%d) @ %d, ask: %d(+%d) @ %d, ok: %d @ %d' % (
        quote['bidSize'], quote['bidDepth'], quote['bid'], quote['askSize'],
        quote['askDepth'], quote['ask'], quote['lastSize'], quote['last']))
    time.sleep(1)
