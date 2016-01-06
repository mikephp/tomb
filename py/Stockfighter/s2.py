#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import gevent
from gevent import monkey
monkey.patch_all()

from stockfighter import Stockfighter
import time

st = Stockfighter.start_level('chock_a_block')
ACCOUNT = st['account']
VENUE = st['venues'][0]
STOCK = st['tickers'][0]
ft = Stockfighter(VENUE, ACCOUNT)


class Order(object):

    def __init__(self, tid, price, qty):
        self.tid = tid
        self.price = price
        self.qty = qty
        self.invalid = False


class OrderManager(object):

    def __init__(self, ft, size=8)
        self.orders = []
        self.market_price = 0
        self.size = size
        self.ft = ft

    def update_market_price(self, v):
        self.market_price = v
        self.action()

    def new_order(self, price, qty):
        global STOCK
        st = self.ft.order(STOCK, price, qty, 'buy', 'limit')
        tid = st['id']
        order = Order(tid, price, qty)
        self.orders.append(order)

    def del_order(self, order):
        global STOCK
        tid = order.tid
        self.ft.cancel(STOCK, tid)
        order.invalid = True


class MarketWatcher(object):

    def __init__(self, ft):
        self.ft = ft
        self.

    def action(self):
        global STOCK
        quote = self.ft.quote(STOCK)


P = 5386
while True:
    quote = ft.quote(STOCK)
    if not ('bid' in quote and 'ask' in quote):
        time.sleep(1)
        continue
    bid = quote['bid']
    if not P:
        P = bid
    if P > bid:
        P = bid
    else:
        P = int((bid - P) * 0.2 + P)
    size = 10000
    timeout = 5
    price = P
    print 'place limit order: %d @ %d' % (size, price)
    st = ft.order(STOCK, price, size, 'buy', 'limit')
    tid = st['id']
    time.sleep(timeout)
    ft.cancel(STOCK, tid)
    st = ft.order_status(STOCK, tid)
    v = sum(map(lambda x: x['qty'], st['fills']))
    p = sum(map(lambda x: x['qty'] * x['price'], st['fills']))
    if v:
        P -= 50
    else:
        P += 20
