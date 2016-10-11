#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def convert(self, s, numRows):
        """
        :type s: str
        :type numRows: int
        :rtype: str
        """
        if numRows == 1: return s
        (_, c) = self.xth(len(s) - 1, numRows)
        ss = []
        for i in range(0, len(s)):
            (x, y) = self.xth(i, numRows)
            idx = x * c + y
            ss.append((s[i], idx))
        ss.sort(lambda x, y: cmp(x[1], y[1]))
        ss2 = map(lambda x: x[0], ss)
        return ''.join(ss2)

    def xth(self, x, n):
        u = 2 * n - 2
        j = (x / u) * 2 + 1
        i = x % u
        if i >= (n - 1):
            i = u - i
        return (i, j)

if __name__ == '__main__':
    s = Solution()
    print s.convert("PAYPALISHIRING", 3)
