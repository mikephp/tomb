#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def maximalRectangle(self, matrix):
        """
        :type matrix: List[List[str]]
        :rtype: int
        """
        n = len(matrix)
        if n == 0: return 0
        m = len(matrix[0])
        if m == 0: return 0

        # O(n^2 * m), 枚举所有的row pairs.
        # 对于(rx, ry), column mth. 如果m列rx行到ry行均为1的话
        # 则认为1，否则认为0. 这样变为找到最长连续1的区间.
        # csum[m][ry+1] - csum[m][rx] == (ry - rx + 1)来快速判断.

        csum = []
        for i in range(m):
            csum.append([0] * (n + 1))

        for i in range(m):
            csum[i][0] = 0
            for j in range(n):
                csum[i][j+1] = csum[i][j] + int(matrix[j][i])

        # print csum
        def f(rx, ry):
            cnt = 0
            res = 0
            for i in range(m):
                v = csum[i][ry+1] - csum[i][rx]
                if v == (ry - rx + 1):
                    cnt += 1
                    res = max(res, cnt)
                else:
                    cnt  = 0
            return res * (ry - rx + 1)

        res = 0
        for i in range(n):
            for j in range(i, n):
               res = max(res, f(i, j))
        return res

if __name__ == '__main__':
    s = Solution()
    # import numpy as np
    # matrix = map(list, np.array("1 0 1 0 0 1 0 1 1 1 1 1 1 1 1 1 0 0 1 0".split()).reshape((4, 5)))
    # print s.maximalRectangle(matrix)
    print s.maximalRectangle([["1"]])
