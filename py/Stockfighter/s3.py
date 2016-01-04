#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from stockfighter import Stockfighter

st = Stockfighter.start_level('sell_side')
ACCOUNT = st['account']
VENUE = st['venues'][0]
STOCK = st['tickers'][0]

import time
ft = Stockfighter(VENUE, ACCOUNT)
SV = 0
SP = 0
THRESHOLD = 1000
MIN_BATCH = 400
while True:
    quote = ft.quote(STOCK)
    if not ('bid' in quote and 'ask' in quote):
        time.sleep(1)
        continue
    bid = quote['bid']
    ask = quote['ask']
    if SV == 0:
        SP = 0
        SV = 0
    if (SV > THRESHOLD):
        direction = 'sell'
    elif SV == 0 or bid < ((SP / SV) - 60):
        direction = 'buy'
    else:
        direction = 'sell'

    if direction == 'sell':
        price = max(ask, SP / SV + 50)
        size = min(MIN_BATCH, SV)
    else:
        price = bid + 10
        size = max(10, min(MIN_BATCH, THRESHOLD - SV))
    print 'order: %s, %d @ %d' % (direction, size, price)
    st = ft.order(STOCK, price, size, direction, 'limit')
    tid = st['id']
    time.sleep(5)
    ft.cancel(STOCK, tid)
    st = ft.order_status(STOCK, tid)
    sp = sum(map(lambda x: x['qty'] * x['price'], st['fills']))
    sv = sum(map(lambda x: x['qty'], st['fills']))
    print st, sv, sp
    if direction == 'sell':
        SP -= sp
        SV -= sv
    else:
        SP += sp
        SV += sv
    print 'SV = %d' % (SV)
