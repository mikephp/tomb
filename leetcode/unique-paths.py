#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def uniquePaths(self, m, n):
        """
        :type m: int
        :type n: int
        :rtype: int
        """
        from functools import reduce
        import operator
        m -= 1
        n -= 1
        # C(m+n-1 ,n) = (m + n) ... 1 / (n ... 1) * (m ... 1)
        # n + 1 ... (m + n) / m ... 1
        A = reduce(operator.mul, xrange(n + 1, m + n + 1), 1)
        B = reduce(operator.mul, xrange(1, m + 1), 1)
        return A / B
