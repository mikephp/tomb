#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def getRow(self, rowIndex):
        """
        :type rowIndex: int
        :rtype: List[int]
        """
        rowIndex += 1
        r = [1]
        for i in range(rowIndex - 1):
            r2 = []
            r2.append(r[0])
            for i in range(0, len(r) - 1):
                r2.append(r[i] + r[i+1])
            r2.append(r[-1])
            r = r2
        return r
