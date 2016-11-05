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

        # st0[i]表示从i点往后看，最高能卖多少钱.
        st = [0] * len(prices)
        st[-1] = prices[-1]
        for i in range(len(prices) - 1, 0, -1):
            st[i-1] = max(st[i], prices[i-1])

        for i in range(len(prices) - 1, -1, -1):
            st[i] = max(0, st[i] - prices[i])
            if (i + 1) < len(prices):
                st[i] = max(st[i], st[i+1])
        st0 = st

        # st1[i]表示i点往前看，最高能卖多少钱.
        st = [0] * len(prices)
        st[0] = prices[0]
        for i in range(1, len(prices)):
            st[i] = min(st[i-1], prices[i])

        for i in range(0, len(prices)):
            st[i] = max(0, prices[i] - st[i])
            if i > 0:
                st[i] = max(st[i], st[i-1])
        st1 = st

        res = 0
        for i in range(0, len(prices)):
            res = max(res, st0[i] + st1[i])
        return res

if __name__ == '__main__':
    s = Solution()
    print s.maxProfit([2,1,2,0,1])
