#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def largestRectangleArea(self, heights):
        """
        :type heights: List[int]
        :rtype: int
        """
        # TODO(yan): FIX ME. TLE.
        res = 0
        for i in range(0, len(heights)):
            s = heights[i]
            for j in range(i + 1, len(heights)):
                if heights[j] >= heights[i]:
                    s += heights[i]
                else:
                    break
            for j in range(i - 1, -1, -1):
                if heights[j] >= heights[i]:
                    s += heights[i]
                else:
                    break
            res = max(res, s)
        return res
