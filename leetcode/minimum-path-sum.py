#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def minPathSum(self, grid):
        """
        :type grid: List[List[int]]
        :rtype: int
        """
        n = len(grid)
        m = len(grid[0])
        st = [[1 << 31] * m, [1 << 31] * m]
        swt = 0
        st[swt][0] = 0

        for i in range(0, n):
            for j in range(0, m):
                st[1-swt][j] = min(st[swt][j], st[1-swt][j-1] if j > 0 else 1 << 31) + \
                  grid[i][j]
            swt = 1 - swt

        return st[swt][m-1]

if __name__ == '__main__':
    s = Solution()
    print s.minPathSum([[1,3,1],[1,5,1],[4,2,1]])
