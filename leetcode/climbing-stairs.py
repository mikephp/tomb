#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def climbStairs(self, n):
        """
        :type n: int
        :rtype: int
        """
        # x + 2y = n
        # (n-y) ! / (n-2y)! * y !
        # y in range(0, n / 2)

        # precompute.
        st = [1] * (n + 1)
        for i in range(1, n + 1):
            st[i] = st[i-1] * i

        res = 0
        for y in range(0, n / 2 + 1):
            res += st[n-y] / (st[n-2*y] * st[y])
        return res

if __name__ == '__main__':
    s = Solution()
    print s.climbStairs(2)
    print s.climbStairs(3)
