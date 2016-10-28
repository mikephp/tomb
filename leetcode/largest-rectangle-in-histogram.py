#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def largestRectangleArea(self, heights):
        """
        :type heights: List[int]
        :rtype: int
        """
        # res = 0
        # for i in range(0, len(heights)):
        #     s = heights[i]
        #     for j in range(i + 1, len(heights)):
        #         if heights[j] >= heights[i]:
        #             s += heights[i]
        #         else:
        #             break
        #     for j in range(i - 1, -1, -1):
        #         if heights[j] >= heights[i]:
        #             s += heights[i]
        #         else:
        #             break
        #     res = max(res, s)
        # return res

        n = len(heights)
        if n == 0: return 0

        res0 = self.single_side(heights)
        res0.sort(key = lambda x: x[0])

        res1 = self.single_side(heights[::-1])
        res1 = map(lambda x: (n - 1 - x[0], n - 1 - x[1]), res1)
        res1.sort(key = lambda x: x[0])

        res = 0
        for i in range(0, len(heights)):
            h = heights[i]
            (x, y) = res0[i]
            (a, b) = res1[i]
            assert(x == a)
            assert(b <= y)
            res = max((y - b + 1) * h, res)
        return res

    def single_side(self, heights):
        rs = []
        rs.append((heights[0], 0))

        idx = 1
        res = []
        while idx < len(heights):
            if heights[idx] < heights[idx - 1]:
                # cut back to (idx - 1)
                j = len(rs) - 1
                while j >= 0:
                    if rs[j][0] > heights[idx]:
                        res.append((rs[j][1], idx - 1))
                        j -= 1
                    else:
                        break
                rs = rs[:j + 1]
            rs.append((heights[idx], idx))
            idx += 1

        for r in rs:
            (h, off) = r
            res.append((off, len(heights) - 1))
        return res

if __name__ == '__main__':
    s = Solution()
    print s.largestRectangleArea([2,1,5,6,2,3])
    print s.largestRectangleArea([2,1,2])
