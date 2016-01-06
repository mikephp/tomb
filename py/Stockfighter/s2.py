#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import gevent
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool

from stockfighter import Stockfighter
import time

st = Stockfighter.start_level('chock_a_block')
ACCOUNT = st['account']
VENUE = st['venues'][0]
STOCK = st['tickers'][0]
ft = Stockfighter(VENUE, ACCOUNT)
SLEEP = int(open('sleep', 'r').read())


def xround(x): return x / 20 * 20


class Order(object):

    def __init__(self, price, qty):
        self.tid = 0
        self.price = price
        self.qty = qty
        self.filled = 0
        self.diff = 0


class OrderManager(object):

    def __init__(self, ft, max_size=16):
        self.orders = []
        self.market = 0
        self.max_size = max_size
        self.ft = ft

    def update_market_price(self, v):
        self.market = v
        self.action()

    def update_order_status(self):
        global STOCK
        pool = Pool()

        self.orders.sort(lambda x, y: -cmp(x.price, y.price))
        for o in self.orders:
            o.diff = 0
        for o in self.orders[:self.max_size]:
            def f(order):
                st = self.ft.order_status(STOCK, order.tid)
                filled = sum(map(lambda x: x['qty'], st['fills']))
                order.diff = filled - order.filled
                order.filled = filled
            g = gevent.spawn(f, o)
            pool.add(g)
        pool.join()
        # 最低成交价格
        deals = [x.price for x in filter(lambda o: o.diff, self.orders)]
        self.orders = filter(lambda o: o.filled < o.qty, self.orders)

    def action(self):
        global STOCK
        pool = Pool()

        # cancel all orders whose price is higher than market price.
        cancel_orders = filter(
            lambda o: o.price > self.market, self.orders)
        for o in cancel_orders:
            g = gevent.spawn(self.ft.cancel, STOCK, o.tid)
            pool.add(g)
            self.orders.remove(o)

        # place new orders according to market
        price_set = set(map(lambda o: o.price, self.orders))
        print('>>>>> price_set = %s' % (price_set))
        for i in range(8):
            p = self.market - i * 50
            if p in price_set:
                continue
            order = Order(p, 2000)

            def place_new_order(order):
                st = self.ft.order(STOCK, order.price,
                                   order.qty, 'buy', 'limit')
                tid = st['id']
                order.tid = tid
            g = gevent.spawn(place_new_order, order)
            pool.add(g)
            self.orders.append(order)
        pool.join()
        price_set = set(map(lambda o: o.price, self.orders))
        print('<<<<< price_set = %s' % (price_set))


class MarketWatcher(object):

    def __init__(self, ft):
        self.ft = ft

    def watch(self, detail=False):
        global STOCK
        quote = ft.quote(STOCK)
        if not ('bid' in quote and 'ask' in quote):
            return
        print('bid: %d(+%d) @ %d, ask: %d(+%d) @ %d' % (
            quote['bidSize'], quote['bidDepth'], quote['bid'],
            quote['askSize'], quote['askDepth'], quote['ask']))

    def estimate(self, om):
        global STOCK
        book = ft.orderbook(STOCK)
        orders = om.orders
        price_mapping = {x.price: x for x in orders}
        bids = book['bids']
        if not bids:
            return 0
        price = 0
        for b in bids:
            if not b['price'] in price_mapping:
                # market price.
                price = b['price']
                break
            o = price_mapping[b['price']]
            if (o.qty - o.filled) < b['qty']:
                # maybe market price.
                price = b['price']
                break
        return price


def play_watch():
    global ft
    mw = MarketWatcher(ft)
    while True:
        mw.watch(detail=True)
        time.sleep(1)


def play_game():
    global ft
    mw = MarketWatcher(ft)
    om = OrderManager(ft)
    pp = 0
    THRESHOLD = int(open('threshold', 'r').read())
    while True:
        print('====================')
        om.update_order_status()
        p = mw.estimate(om)
        if not p:
            time.sleep(SLEEP)
            continue
        p = xround(p)
        if pp and p > pp:
            p = min(pp + 50, p, THRESHOLD)
        pp = p
        print('market price = %d' % p)
        om.update_market_price(p)
        time.sleep(SLEEP)

if __name__ == '__main__':
    play_game()
