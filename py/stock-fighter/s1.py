#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from stockfighter import Stockfighter

st = Stockfighter.start_level('first_steps')
ACCOUNT = st['account']
VENUE = st['venues'][0]
STOCK = st['tickers'][0]

ft = Stockfighter(VENUE, ACCOUNT)
st = ft.order(STOCK, 100, 100, 'buy', 'market')
print(st)
