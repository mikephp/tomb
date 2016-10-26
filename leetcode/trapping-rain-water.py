#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def trap(self, height):
        if not height: return 0

        # 从中间划分，从不同方向看形成两个岭(ridge)
        max_idx = None
        max_h = -1
        for (i,h) in enumerate(height):
            if h > max_h:
                max_idx = i
                max_h = h
        return self._trap(height[:max_idx + 1]) + self._trap(height[max_idx:][::-1])

    def _trap(self, height):
        """
        :type height: List[int]
        :rtype: int
        """
        if len(height) <= 2: return 0
        res = 0
        i = 0
        while i < len(height):
            j = i + 1
            while j < len(height) and height[j] < height[i]: j += 1
            h = height[i]
            for k in range(i, j):
                # print 'aread from {} to {}. h = {}'.format(i, j, h)
                res += (h - height[k])
            (i, j) = (j, j + 1)
        return res

if __name__ == '__main__':
    s = Solution()
    print s.trap([4,2,3])
    print s.trap([0,1,0,2,1,0,1,3,2,1,2,1])
    print s.trap([6,4,2,0,3,2,0,3,1,4,5,3,2,7,5,3,0,1,2,1,3,4,6,8,1,3])
