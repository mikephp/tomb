#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

# http://inclass.kaggle.com/c/ml-course-internal-competition

import os
import numpy as np

def read_ft(fname):
    f = open(fname)
    xs = []
    for s in f:
        s = s.strip()
        xs.append(map(lambda x: int(x),s.split(' ')))
    f.close()
    # 选择横竖以及正反对角线上1的分布作为feature.
    n = len(xs)
    xs2 = []
    for i in range(0, n):
        v = 0
        for j in range(0, n): v += xs[i][j]
        xs2.append(v)
    for j in range(0, n):
        v = 0
        for i in range(0, n): v += xs[i][j]
        xs2.append(v)
    tk = n
    for r in range(tk, -1, -1):
        v = 0
        c = 0
        while r < n:
            v += xs[r][c]
            c += 1; r += 1
        xs2.append(v)
    for c in range(0, tk):
        v = 0
        r = 0
        while c < n:
            v += xs[r][c]
            r += 1; c += 1
        xs2.append(v)
    for c in range(0, tk):
        v = 0
        r = 0
        while c >= 0:
            v += xs[r][c]
            r += 1; c -= 1
        xs2.append(v)
    for r in range(0, tk):
        v = 0
        c = 0
        while r < n:
            v += xs[r][c]
            r += 1; c -= 1
        xs2.append(v)
    xs3 = [0] * (n+1)
    for x in xs2:
        xs3[x] += 1
    return np.array(xs3)

# 训练数据
def load_tr():
    ys = []
    xs = []
    mp = [1,2,3]
    for p in mp:
        tag = str(p)
        for f in os.listdir('tr/' + tag):
            ys.append(p)
            x = read_ft('tr/' + tag + '/' + f)
            xs.append(x)
    return (np.array(xs), np.array(ys))

# 测试数据
def load_tt():
    xs = []
    for f in range(1, 31):
        x = read_ft('tt/' + str(f) + '.txt')
        xs.append(x)
    return np.array(xs)

from sklearn import svm
from sklearn.svm import SVC
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report

def train(tr):
    (X, Y) = tr

    # 使用cross validation来做参数选择
    tuned_parameters = [{'kernel':['linear'], 'C':[1, 10, 100]},                        
                        {'kernel': ['rbf'], 'gamma': [1e-4, 1e-3, 1e-2], 'C': [1, 10, 100]}]
    clf = GridSearchCV(SVC(), tuned_parameters, cv = 10)
    clf.fit(X, Y)
    print("Best parameters set found on development set:")
    print(clf.best_estimator_)
    print("Grid scores on development set:")
    for params, mean_score, scores in clf.grid_scores_:
        print("%0.3f (+/-%0.03f) for %r" % (mean_score, scores.std() *2 , params))
    # 选择最好的分类器
    clf = clf.best_estimator_

    # 看看最好分类器效果如何
    tr_x, tt_x, tr_y, tt_y = train_test_split(X, Y, test_size = 0.2, random_state = 0)
    clf.fit(tr_x, tr_y)
    print("Detailed classification report:")
    print("The model is trained on the full development set.")
    print("The scores are computed on the full evaluation set.")
    y_true, y_pred = tt_y, clf.predict(tt_x)
    print(classification_report(y_true, y_pred))

    # 使用全部数据集合来训练最终模型.
    clf.fit(X, Y)
    return clf

def test(clf, tt):
    y_pred = clf.predict(tt)
    f = open('submission.csv','w')
    f.write('Id,Prediction\n')
    for i in range(1, 31):
        f.write('%d,%d\n' % (i, y_pred[i-1]))
    f.close()

def main():
    print('loading training set ...')
    tr = load_tr()
    print('loading test set ...')
    tt = load_tt()
    print('training ...')
    clf = train(tr)
    print('testing ...')
    test(clf, tt)

if __name__ == '__main__':
    main()
