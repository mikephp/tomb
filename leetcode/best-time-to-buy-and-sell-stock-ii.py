#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def maxProfit(self, prices):
        """
        :type prices: List[int]
        :rtype: int
        """
        if not prices: return 0
        res = 0
        a = prices[0]
        b = prices[0]
        for i in range(1, len(prices)):
            p = prices[i]
            if p < b:
                res += (b - a)
                a = p
                b = p
            else:
                b = p
        res += (b - a)
        return res
