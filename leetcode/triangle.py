#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def minimumTotal(self, triangle):
        """
        :type triangle: List[List[int]]
        :rtype: int
        """
        for i in range(1, len(triangle)):
            for j in range(0, i + 1):
                r0 = triangle[i-1][j-1] if j > 0 else 1 << 31
                r1 = triangle[i-1][j] if j != i else 1 << 31
                triangle[i][j] += min(r0, r1)
        return min(triangle[-1])
