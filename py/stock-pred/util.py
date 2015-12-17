#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from yahoo_finance import Share
import os
import json
def fetch_data(code, date_from, date_to):
    path = '%s-%s-%s.json' % (code, date_from, date_to)
    if os.path.exists(path):
        with open(path) as fh:
            s = open(path).read()
            return json.loads(s)
    print('fetch data of %s (%s - %s)' % (code, date_from, date_to))
    share = Share(code)
    data = share.get_historical(date_from, date_to)
    with open(path, 'w') as fh:
        fh.write(json.dumps(data))
        return data

import numpy as np
def adj_close(data):
    return np.array(map(lambda x: float(x['Adj_Close']), data))
def volumes(data):
    return np.array(map(lambda x: float(x['Volume']), data))

if __name__ == '__main__':
    baba = fetch_data('BABA', '2015-01-16', '2015-12-16')
    close_prices = adj_close(baba)
    
