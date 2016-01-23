#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from config import *

from gevent import monkey
monkey.patch_all()

import os
import json

import pymongo
from pymongo import MongoClient
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
            v = np.array(map(lambda x: x[key], data)).reshape(-1, 1)
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

if __name__ == '__main__':
    dt_from = dt.datetime(2014, 1, 1)
    dt_to = dt.datetime(2016, 1, 22)

    d = stock_data(dt_from, dt_to, ['BABA', 'JD', 'GOOG'])
    print d['BABA']
