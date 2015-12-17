#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from util import *
import traceback
import pdb
LOOKAHEAD = 10
INTERVALS = [1,2,3,5]
def feature(pts, f):
    pts = pts[f+1: f+LOOKAHEAD+1]
    fts = np.array([])
    for it in INTERVALS:
        r = (pts[:-it] - pts[it:]) / (pts[it:] + 1)
        fts = np.append(fts, r)
    return fts

def target(pts, f):
    r = (pts[f] - pts[f+1]) / pts[f+1]
    if r > 0.05: return 4
    elif r > 0.025: return 3
    elif r > 0.01: return 2
    elif r > 0: return 1
    else: return 0
    # if pts[f] > pts[f+1]: return 1
    # else: return 0

def xy_data(close_prices, close_volumes, f, t):
    X = []
    Y = []
    for i in xrange(f, t):
        # X.append(np.append(feature(close_prices, i), feature(close_volumes, i)))
        X.append(feature(close_prices, i))
        Y.append(target(close_prices, i))
    return X, Y

def xy_code(code, s, e, train_ratio = 0.8):
    data = fetch_data(code, s, e)
    size = len(data) - LOOKAHEAD
    close_prices = adj_close(data)
    close_volumes = volumes(data)
    pivot = int(size * (1 - train_ratio))
    train_data = xy_data(close_prices, close_volumes, pivot + LOOKAHEAD, size)
    test_data = xy_data(close_prices, close_volumes, 0, pivot)
    return (train_data, test_data)

def aug_xy(XY, xy):
    (X, Y) = XY
    (x, y) = xy
    X.extend(x)
    Y.extend(y)
