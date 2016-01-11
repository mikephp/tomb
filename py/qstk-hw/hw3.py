#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def simulate(orders, amount):
    dt_timeofday = dt.timedelta(hours=16)
    dt_start = orders[0][0]
    dt_end = orders[-1][0]
    # print(dt_start, dt_end)
    ls_symbols = list(set(map(lambda x: x[1], orders)))
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(
        dt_start, dt_end + dt.timedelta(hours=24), dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    df_price = ldf_data[0]
    cash = amount
    stocks = {}
    values = []
    order_idx = 0
    for ts in ldt_timestamps:
        date = dt.datetime(ts.year, ts.month, ts.day)
        while order_idx < len(orders) and orders[order_idx][0] == date:
            o = orders[order_idx]
            (_, sym, direction, qty) = o
            price = df_price[sym].ix[ts]
            if direction == 'Buy':
                cash -= price * qty
                if sym in stocks:
                    stocks[sym] += qty
                else:
                    stocks[sym] = qty
            else:
                cash += price * qty
                stocks[sym] -= qty
            order_idx += 1
        total = cash
        for sym in stocks.keys():
            qty = stocks[sym]
            price = df_price[sym].ix[ts]
            total += qty * price
        values.append((date, total))
    return values


def read_orders(fname):
    with open(fname) as fh:
        orders = []
        for s in fh:
            (year, mon, day, sym, direction, qty, _) = s.strip().split(',')
            date = dt.datetime(int(year), int(mon), int(day))
            orders.append((date, sym, direction, int(qty)))
        return orders


def write_values(values, fname):
    with open(fname, 'w') as fh:
        lines = map(lambda x: '%d,%d,%d,%d\n' %
                    (x[0].year, x[0].month, x[0].day, x[1]), values)
        fh.writelines(lines)


if __name__ == '__main__':
    orders = read_orders('orders-short.csv')
    # print(orders)
    values = simulate(orders, 1000000)
    write_values(values, 'values-short2.csv')
