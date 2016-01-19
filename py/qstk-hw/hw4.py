#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

import hw3


PRICE = 5.0


def find_events(ls_symbols, d_data, orders):
    ''' Finding the event dataframe '''
    # df_close = d_data['close']
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    global PRICE
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (
                f_marketprice_today / f_marketprice_yest) - 1

            # Event is found if the symbol is down more then 3% while the
            # market is up more then 2%

            if (f_symreturn_today <= -0.03 and f_marketreturn_today >= 0.02):
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

            # if f_symprice_yest >= PRICE and f_symprice_today < PRICE:
            # df_events[s_sym].ix[ldt_timestamps[i]] = 1

                buy_ts = ldt_timestamps[i]
                idx = (i + 12)
                if idx >= len(ldt_timestamps):
                    sell_ts = ldt_timestamps[-1]
                else:
                    sell_ts = ldt_timestamps[idx]
                orders.append((buy_ts, s_sym, 'Buy', 100))
                orders.append((sell_ts, s_sym, 'Sell', 100))

    return df_events


def event_study(dt_start, dt_end):
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    orders = []
    df_events = find_events(ls_symbols, d_data, orders)
    with open('hw4-orders.csv', 'w') as fh:
        lines = []
        for order in orders:
            (ts, sym, direction, amount) = order
            lines.append('%d,%d,%d,%s,%s,%d,\n' %
                         (ts.year, ts.month, ts.day, sym, direction, amount))
        fh.writelines(lines)

    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                     s_filename='hw4.pdf', b_market_neutral=True, b_errorbars=True,
                     s_market_sym='SPY')


def test_performance():
    orders = hw3.read_orders('hw4-orders.csv')
    (ldt_timestamps, values) = hw3.simulate(orders, 50000)
    # hw3.output_values(ldt_timestamps, values)
    hw3.compare_to_SPX(ldt_timestamps, values, 'hw4-compare-spx.pdf')


def main():
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    # global PRICE
    # for p in [6, 7, 8, 9, 10]:
    #     PRICE = p
    #     event_study(dt_start, dt_end)
    #     print('===== price threshold %d =====' % (p))
    #     test_performance()
    event_study(dt_start, dt_end)
    test_performance()

if __name__ == '__main__':
    main()
