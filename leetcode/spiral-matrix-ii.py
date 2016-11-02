#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def generateMatrix(self, n):
        """
        :type n: int
        :rtype: List[List[int]]
        """
        res = []
        (i, j, v) = (0, 0, 1)
        m = n
        # print '---'
        while True:
            # print (i, j) , (i, m-1-j) , (n-1-i, m-1-j) , (n-1-i, j)
            for c in range(j, m - j):
                res.append((i, c, v))
                v += 1
            if v > n * n: break

            for r in range(i + 1, n - i):
                res.append((r, m-1-j, v))
                v += 1
            if v > n * n: break

            for c in range(m-2-j, j-1, -1):
                res.append((n-1-i, c, v))
                v += 1
            if v > n * n: break

            for r in range(n-2-i, i, -1):
                res.append((r, j, v))
                v += 1
            if v > n * n: break

            i += 1
            j += 1

        res.sort(lambda x, y: cmp(x[0], y[0]) or cmp(x[1], y[1]))

        m = []
        for i in range(0, n):
            m.append([0] * n)
            for j in range(0, n):
                m[-1][j] = res[i * n + j][2]
        return m

if __name__ == '__main__':
    s = Solution()
    print s.generateMatrix(3)
    print s.generateMatrix(8)    
