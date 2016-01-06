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
SLEEP = 3


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
        # 最低成交价格. 最低成交价格有可能是当前市场价.
        deals = [x.price for x in filter(lambda o: o.diff, self.orders)]
        self.orders = filter(lambda o: o.filled < o.qty, self.orders)
        price = 0 if not deals else deals[-1]  # min
        # price = 0 if not deals else deals[0]  # max
        return price

    def action(self):
        global STOCK
        pool = Pool()

        # 取消所有高于市场价格的订单.
        cancel_orders = filter(
            lambda o: o.price > self.market, self.orders)
        for o in cancel_orders:
            g = gevent.spawn(self.ft.cancel, STOCK, o.tid)
            pool.add(g)
            self.orders.remove(o)

        # 根据当前市场投放新订单
        price_set = set(map(lambda o: o.price, self.orders))
        print('>>>>> price_set = %s' % (price_set))
        for i in range(4):
            p = self.market - i * 40
            if p in price_set:
                continue
            order = Order(p, 250)  # 只购买250, 小单.

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
        # 根据自己投放订单估算市场价格.
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


# 这种办法是假设不知道阈值是多少. 偶尔可以成功，但是加上阈值则会保险不少.
# 尽可能地估计准确market price. 同样应该尽可能地多下单.
def play_game1():
    global ft
    mw = MarketWatcher(ft)
    om = OrderManager(ft)
    pp = 0
    THRESHOLD = int(raw_input('target price > '))
    while True:
        print('====================')
        # 根据成交情况算出
        p0 = om.update_order_status()
        # 根据orderbook算出
        p1 = mw.estimate(om)
        if not p0 and not p1:
            p = 0
        elif p0 and p1:
            p = min(p0, p1)
        else:
            p = p0 or p1
        if not p:
            if pp:
                p = pp
            else:
                p = THRESHOLD
        # 市场价格不能波动太大, 并且要小于某个阈值.
        if pp and p > pp:
            p = min(pp + 40, p)
        p = min(p, THRESHOLD)
        pp = p

        # 为了加快完成，需要让出部分profit.
        margin = (THRESHOLD - p)
        ratio = 0.4
        p = int(margin * ratio) + p
        p = xround(p)
        print('market price = %d' % p)
        om.update_market_price(p)
        time.sleep(SLEEP)


# so effective...
# 为了知道这个threshold, 可以先在web上放个market order, 买入10股，
# 然后web界面就会显示target price. 只要下单足够快，价格就会保持在那个位置上.
# 虽然可以很快完成交易，但是如果以target price来下单的话，cost则会相对较高，
# 所以分数也就更低.
def play_game2():
    global STOCK
    THRESHOLD = int(raw_input('target price > '))
    price = THRESHOLD
    size = 500
    while True:
        st = ft.order(STOCK, price, size, 'buy', 'limit')
        tid = st['id']
        while True:
            st = ft.order_status(STOCK, tid)
            filled = sum(map(lambda x: x['qty'], st['fills']))
            if filled == size:
                break
            time.sleep(SLEEP)

if __name__ == '__main__':
    play_game1()
