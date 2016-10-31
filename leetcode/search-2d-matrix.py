#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def searchMatrix(self, matrix, target):
        """
        :type matrix: List[List[int]]
        :type target: int
        :rtype: bool
        """
        n = len(matrix)
        if n == 0: return False
        n2 = len(matrix[0])
        if n2 == 0: return False

        s, e = 0, n - 1
        while s <= e:
            m = (s + e) / 2
            if matrix[m][0] == target:
                return True
            elif matrix[m][0] > target:
                e = m - 1
            else:
                s = m + 1
        r = e

        s, e = 0, n2 - 1
        while s <= e:
            m = (s + e) / 2
            if matrix[r][m] == target:
                return True
            elif matrix[r][m] > target:
                e = m - 1
            else:
                s = m + 1
        return False

if __name__ == '__main__':
    s = Solution()
    print s.searchMatrix([[1],[3],[5]], 4)
