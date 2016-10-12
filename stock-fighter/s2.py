#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from gevent import monkey
monkey.patch_all()
import gevent
from gevent.pool import Pool

from stockfighter import Stockfighter
import time

st = Stockfighter.start_level('chock_a_block')
ACCOUNT = st['account']
VENUE = st['venues'][0]
STOCK = st['tickers'][0]
ft = Stockfighter(VENUE, ACCOUNT)

# put 10 qty market order first manually.

def play():
    global STOCK
    price = int(raw_input('target price > '))
    size = 500
    while True:
        st = ft.order(STOCK, price, size, 'buy', 'limit')
        tid = st['id']
        while True:
            st = ft.order_status(STOCK, tid)
            filled = sum(map(lambda x: x['qty'], st['fills']))
            if filled == size:
                break
            time.sleep(0.5)

if __name__ == '__main__':
    play()
