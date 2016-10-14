#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    # def maxArea(self, height):
    #     """
    #     :type height: List[int]
    #     :rtype: int
    #     """
    #     res = 0
    #     i = 0
    #     while (i + 1) < len(height):
    #         j = i + 1
    #         maxj = -1
    #         while j < len(height):
    #             if maxj == -1 or height[j] >= height[maxj]:
    #                 maxj = j
    #             if height[j] >= height[i]:
    #                 break
    #             j += 1
    #         res += min(height[i], height[maxj]) * (maxj - i)
    #         i = maxj
    #     return res

    def maxArea0(self, height):
        """
        :type height: List[int]
        :rtype: int
        """
        hs = [[h, idx] for (idx, h) in enumerate(height)]
        hs.sort(lambda x, y: cmp(x[0], y[0]) or cmp(x[1], y[1]))
        for i in range(len(hs) - 1, 0, -1):
            hs[i-1][1] = max(hs[i-1][1], hs[i][1])
        d = {}
        for (h, idx) in hs:
            d[h] = idx
        res = 0
        for (i, h) in enumerate(height):
            j = d[h]
            res = max(res, h * (j - i))
        return res

    def maxArea(self, height):
        return max(self.maxArea0(height), self.maxArea0(height[::-1]))
