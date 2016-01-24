#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from gevent import monkey
monkey.patch_all()

import os
import json

import pymongo
from pymongo import MongoClient
MONGO_URL = 'mongodb://127.0.0.1:27017'
Client = MongoClient(MONGO_URL)
DB = Client.stock_pred
TStockHistory = DB.history
TStockHistory.create_index('Symbol')
TStockHistory.create_index([('Symbol', pymongo.ASCENDING),
                          ('Date', pymongo.DESCENDING)])


import gevent
from gevent.pool import Pool

from yahoo_finance import Share
import datetime as dt
import dateutil.parser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Document(object):

    """Mongo Document"""

    @classmethod
    def from_json(cls, js):
        x = cls()
        x.__dict__ = js
        return x

    def to_json(self):
        return self.__dict__


def fetch_data(dt_from, dt_to, sym):
    min_dt_from = dt.datetime(2014, 1, 1)
    assert(dt_from >= min_dt_from)
    r = TStockHistory.find_one(
        {'Symbol': sym}, projection={'Date': 1}, sort=[('Date', pymongo.DESCENDING)])
    if not r:
        fetch_dt_from = min_dt_from
    elif r['Date'] < dt_to:
        fetch_dt_from = r['Date'] + dt.timedelta(days=1)
    else:
        fetch_dt_from = None
    if fetch_dt_from:
        f = '%d-%d-%d' % (
            fetch_dt_from.year, fetch_dt_from.month, fetch_dt_from.day)
        t = '%d-%d-%d' % (dt_to.year, dt_to.month, dt_to.day)
        print('fetch %s from network...' % (sym))
        share = Share(sym)
        docs = share.get_historical(f, t)
        if docs:
            for r in docs:
                for k in ['Adj_Close', 'High', 'Low', 'Close', 'Volume']:
                    r[k] = np.float(r[k])
                r['Date'] = dateutil.parser.parse(r['Date'])
            if docs[-1]['Date'] != dt_to:
                docs.append({'Date': dt_to, 'placeholder': 1})
            TStockHistory.insert_many(docs)
    data = TStockHistory.find(
        {'Symbol': sym, 'Date': {'$gte': dt_from, '$lte': dt_to}})
    rs = filter(lambda x: 'placeholder' not in x, [u for u in data])
    return rs


def stock_data(dt_from, dt_to, ls_symbols):
    ls_keys = ['Open', 'Close', 'High', 'Low', 'Volume', 'Adj_Close']
    d = {}

    def f(sym):
        data = fetch_data(dt_from, dt_to, sym)
        dates = map(lambda x: x['Date'], data)
        values = []
        for key in ls_keys:
            v = np.array(map(lambda x: np.float(x[key]), data)).reshape(-1, 1)
            values.append(v)
        values = np.hstack(values)
        df = pd.DataFrame(values, index=dates, columns=ls_keys)
        d[sym] = df

    pool = Pool(size=8)
    for sym in ls_symbols:
        g = gevent.spawn(f, sym)
        pool.add(g)
    pool.join()
    return d


def returnize0(nds):
    """
    @summary Computes stepwise (usually daily) returns relative to 0, where
    0 implies no change in value.
    @return the array is revised in place
    """
    if type(nds) == type(pd.DataFrame()):
        nds = (nds / nds.shift(1)) - 1.0
        nds = nds.fillna(0.0)
        return nds

    s = np.shape(nds)
    if len(s) == 1:
        nds = np.expand_dims(nds, 1)
    nds[1:, :] = (nds[1:, :] / nds[0:-1]) - 1
    nds[0, :] = np.zeros(nds.shape[1])
    return nds


def _price(d_data, key):
    values = map(lambda x: pd.Series(d_data[x][key], name=x), d_data)
    return pd.concat(values, axis=1)


def actual_close_price(d_data):
    return _price(d_data, 'Close')


def close_price(d_data):
    return _price(d_data, 'Adj_Close')


def bollinger_band(df_price, lookback=20, ratio=2):
    df_mean = pd.rolling_mean(df_price, lookback)
    df_std = pd.rolling_std(df_price, lookback)
    df_bb_ratio = (df_price - df_mean) / (ratio * df_std)
    df_high = df_mean + ratio * df_std
    df_low = df_mean - ratio * df_std
    return (df_mean, df_high, df_low, df_bb_ratio)


def reverse_bollinger_band(df_price, ratio=2):
    A = df_price.shape[0] + 1
    B = ratio
    mean = np.mean(df_price, axis=0)
    std = np.std(df_price, axis=0)
    C = (A - 1) * mean
    D = (A - 1) * (std ** 2 + mean ** 2)
    B2 = B ** 2
    a = (B2 - (A - 1)) * (A - 1)
    b = 2 * C * (A - B2 - 1)
    c = A * B2 * D - (B2 + 1) * (C ** 2)

    common = np.sqrt(b ** 2 - 4 * a * c)
    r0 = (common - b) * 0.5 / a
    r1 = (-common - b) * 0.5 / a
    return (r0, r1)

if __name__ == '__main__':
    dt_from = dt.datetime(2014, 1, 1)
    dt_to = dt.datetime(2016, 1, 22)

    d = stock_data(dt_from, dt_to, ['BABA', 'JD', 'GOOG'])
    print d['BABA']
