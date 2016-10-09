#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def findMedianSortedArrays(self, nums1, nums2):
        """
        :type nums1: List[int]
        :type nums2: List[int]
        :rtype: float
        """
        m = len(nums1)
        n = len(nums2)
        if (m + n) % 2 == 0:
            b = self.Xth(nums1, nums2, (m+n)/2-1)
            a = self.Xth(nums1, nums2, (m+n)/2)
            return (a + b) * 0.5
        else:
            return self.Xth(nums1, nums2, (m+n)/2)

    def Xth(self, nums1, nums2, x):
        v = self.xth(nums1, nums2, x)
        if v: return v
        return self.xth(nums2, nums1, x)

    def xth(self, nums1, nums2, x):
        (s, e) = (0, len(nums1) - 1)
        while s <= e:
            m = (s + e) / 2
            a = nums1[m]
            L = self.bs(nums2, a, 'low')
            R = self.bs(nums2, a, 'high')
            if (m + L) <= x and x <= (m + R):
                # print 'OK'
                return a
            elif (m + L) < x:
                s = m + 1
            else:
                e = m - 1
        return None

    def bs(self, xs, x, eq = 'exact'):
        (s, e) = (0, len(xs) - 1)
        while s <= e:
            m = (s + e) / 2
            if xs[m] == x:
                if eq == 'low':
                    e = m - 1
                elif eq == 'high':
                    s = m + 1
                else:
                    return m
            elif xs[m] < x:
                s = m + 1
            else:
                e = m - 1
        return s

if __name__ == '__main__':
    s = Solution()
    print s.bs([1,3,5,7,9], 6)
    print s.xth([1,3,5,7,9],[2,4,6,8,10],4)
    print s.xth([1,3,5,7,9],[2,4,6,8,10],5)
    print s.xth([2,4,6,8,10],[1,3,5,7,9],4)
    print s.xth([2,4,6,8,10],[1,3,5,7,9],5)
    print s.findMedianSortedArrays([1,3],[2])
    print s.findMedianSortedArrays([1,2],[3,4])
    print s.findMedianSortedArrays([1],[1])
