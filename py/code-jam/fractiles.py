#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import sys
fh = sys.stdin
case_num = int(fh.readline())

"""
这个问题我的想法考虑一个通用情况, 假设original tiles长度是k. 假设在0th, (i-1)th, (j-1)th是G的话，
分别考虑C=2,C=3的时候，应该在哪个点clean是最优解. 如果C=3的话，那么三个G会共同出现在一个位置上，就是0 * k^2 + (i-1) *k + (j-1)
以此类推，如果C=K的话，那么所有可能的G都会出现在一点上.
"""

def f(K, C, S):
    group = (K - C + 1)
    if S < group:
        return 'IMPOSSIBLE'
    res = []
    x = 0
    for i in range(1, min(C, K)):
        x = x * K + i
    res.append(x + 1)
    for i in range(C, K):
        res.append(i + 1)
    return ' '.join(map(lambda x: str(x), res))

for c in range(case_num):
    (K, C, S) = map(lambda x: int(x), fh.readline().split())
    res = f(K, C, S)
    print('Case #%d: %s' % (c + 1, res))
