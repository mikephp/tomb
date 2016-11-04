#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def generate(self, numRows):
        """
        :type numRows: int
        :rtype: List[List[int]]
        """
        res = []
        if not numRows: return res
        res.append([1])
        for i in range(numRows - 1):
            r = res[-1]
            r2 = []
            r2.append(r[0])
            for i in range(0, len(r) - 1):
                r2.append(r[i] + r[i+1])
            r2.append(r[-1])
            res.append(r2)
        return res
