#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from feature import *

from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score

# clf = RandomForestRegressor(100, random_state = 1)
clf = RandomForestClassifier(400, random_state = 1, min_samples_leaf = 2)
codes = ['BABA', 'AAPL', 'JD', 'GOOG', 'MSFT', 'INTC', 'CSCO', 'NVDA', 'TWTR', 'FB', 'BIDU', 'TLSA']
train_data = ([], [])
test_data = ([], [])
for code in codes:
    (tr, tt) = xy_code(code, '2014-01-01', '2015-12-16')
    aug_xy(train_data, tr)
    aug_xy(test_data, tt)
print len(train_data[0]), len(train_data[1]), len(test_data[0]), len(test_data[1])

clf.fit(train_data[0], train_data[1])
Y = clf.predict(test_data[0])
print accuracy_score(Y, test_data[1])
