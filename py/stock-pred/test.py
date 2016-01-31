#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import util
import pandas as pd
import numpy as np
import datetime as dt


def get_stock_data(ls_symbols):
    dt_start = dt.datetime(2014, 1, 1)
    dt_end = dt.datetime.today()
    d_data = util.stock_data(dt_start, dt_end, ls_symbols)
    return d_data


def buy_or_sell_price():
    print('=====buy or sell price=====')
    ls_symbols = ['JD', 'TEAM', 'NFLX', 'FB', 'AAPL']
    d_data = get_stock_data(ls_symbols)
    df_price = util.close_price(d_data)
    print(df_price[-20:-1])
    for r in (1, 1.5, 2):
        print('>>> ratio = %.2f <<<' % r)
        (buy, sell) = util.reverse_bollinger_band(df_price[-20:-1], ratio=r)
        for sym in ls_symbols:
            print('%5s: buy@%.2f sell@%.2f' % (sym, buy[sym], sell[sym]))


def sharpe_ratio():
    print('=====sharpe ratio=====')
    ls_symbols = ['AAPL', 'AMZN', 'GOOG', 'FB',
                  'MSFT', 'SPY', 'NFLX', 'BABA', 'JD']
    d_data = get_stock_data(ls_symbols)
    df_price = util.close_price(d_data)[-120:]
    df_rets = util.returnize0(df_price)
    df_mean = np.mean(df_rets)
    df_std = np.std(df_rets)
    sr = df_mean / df_std
    rs = zip(sr.index, sr.values)
    rs.sort(lambda x, y: -cmp(x[1], y[1]))
    for (sym, v) in rs:
        print('%5s: %.4f' % (sym, v))

if __name__ == '__main__':
    buy_or_sell_price()
    sharpe_ratio()
