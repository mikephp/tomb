#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def search(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: int
        """
        p = self.locate_pivot(nums)
        a = self.bs_locate(nums, 0, p, target)
        if a != -1: return a
        a = self.bs_locate(nums, p + 1, len(nums) - 1, target)
        if a != -1: return a
        return -1

    def bs_locate(self, nums, s, e, target):
        while s <= e:
            m = (s + e) / 2
            if nums[m] == target:
                return m
            elif nums[m] > target:
                e = m - 1
            else:
                s = m + 1
        return -1

    # pivot is a[i] > a[i-1] and a[i] > a[i+1]
    def locate_pivot(self, nums):
        (s, e) = (0, len(nums) - 1)

        # make sure 3 elements.
        while (e - s) >= 2:
            # print (s, e)
            m = (s + e) / 2
            # 100 percent sure.
            if ((m - 1) >= 0 and nums[m] > nums[m - 1]) and \
                ((m + 1) < len(nums) and nums[m] > nums[m + 1]):
                 return m

            if nums[m] > nums[e]:
                s = m
            else:
                e = m

        # special cases.
        if (e - s) == 1:
            if nums[s] < nums[e]: return e
            else: return s
        else:
            return s

if __name__ == '__main__':
    s = Solution()
    print s.locate_pivot([4,5,6,7,0,1,2])
    print s.locate_pivot([2, 0, 1])
    print s.search([4,5,6,7,0,1,2], 2)
    print s.locate_pivot([1,3])
    print s.search([1,3], 0)
    print s.locate_pivot([1])
    print s.search([1], 0)
    print s.locate_pivot([8,9,2,3,4])
    print s.locate_pivot([4,5,6,7,8,1,2,3])
