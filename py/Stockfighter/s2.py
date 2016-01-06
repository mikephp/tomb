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


class Order(object):

    def __init__(self, price, qty):
        self.tid = 0
        self.price = price
        self.qty = qty
        self.filled = 0


class OrderManager(object):

    def __init__(self, ft, max_size=8):
        self.orders = []
        self.market = 0
        self.max_size = max_size
        self.ft = ft
        self.step = 20

    def update_market_price(self, v):
        self.market = (v / self.step) * self.step
        print('market = %d' % (self.market))
        self.action()

    def action(self):
        pool = Pool()
        global STOCK

        # cancel all orders whose price is higher than market
        cancel_orders = filter(lambda o: o.price > self.market, self.orders)
        for o in cancel_orders:
            g = gevent.spawn(self.ft.cancel, STOCK, o.tid)
            pool.add(g)
            self.orders.remove(o)
        # check all orders which are filled and remove them.
        for o in self.orders:
            def check_filled_cond(order):
                st = self.ft.order_status(STOCK, order.tid)
                filled = sum(map(lambda x: x['qty'], st['fills']))
                self.filled = filled
            g = gevent.spawn(check_filled_cond, o)
            pool.add(g)
        pool.join()
        self.orders = filter(lambda o: o.filled < o.qty, self.orders)

        # place new orders according to market
        price_set = set(map(lambda o: o.price, self.orders))
        print('>>>>> price_set = {}'.format(price_set))
        for i in range(10):
            p = self.market - i * self.step
            if p in price_set:
                continue
            order = Order(p, 1000)

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
        print('<<<<< price_set = {}'.format(price_set))


class MarketWatcher(object):

    def __init__(self, ft):
        self.ft = ft
        self.market_price = 0

    def watch(self, detail=False):
        global STOCK
        quote = ft.quote(STOCK)
        if not ('bid' in quote and 'ask' in quote):
            return self.market_price
        if detail:
            print('bid: %d(+%d) @ %d, ask: %d(+%d) @ %d' % (
                quote['bidSize'], quote['bidDepth'], quote['bid'],
                quote['askSize'], quote['askDepth'], quote['ask']))
        bid = quote['bid']
        if not self.market_price:
            self.market_price = bid
        elif self.market_price > bid:
            self.market_price = bid
        else:
            self.market_price = min(self.market_price + 100, bid)
        return self.market_price


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
    while True:
        p = mw.watch()
        if not p:
            time.sleep(1)
        om.update_market_price(p)

if __name__ == '__main__':
    play_game()
