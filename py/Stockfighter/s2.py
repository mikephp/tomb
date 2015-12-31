#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from stockfighter import Stockfighter

st = Stockfighter.start_level('chock_a_block')
ACCOUNT = st['account']
VENUE = st['venues'][0]
STOCK = st['tickers'][0]

# ACCOUNT = 'DAH75681156'
# VENUE = 'FFDEX'
# STOCK = 'DOIN'

import time
ft = Stockfighter(VENUE, ACCOUNT)
P = 0
while True:
    quote = ft.quote(STOCK)
    if not ('bid' in quote and 'ask' in quote): time.sleep(1); continue
    bid = quote['bid']
    ask = quote['ask']
    if not P: P = bid
    if P > bid:
        P -= 50
    else:
        P += 50
    size = max(10000, quote['bidSize'])
    price = P
    print 'place limit order: %d @ %d' % (size, price)
    st = ft.order(STOCK, price, size, 'buy', 'limit')
    tid = st['id']
    time.sleep(5)
    st = ft.order_status(STOCK, tid)
    v = sum(map(lambda x : x['qty'], st['fills']))
    if v < size: ft.cancel(STOCK, tid)
