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
        if a != -1: return True
        a = self.bs_locate(nums, p + 1, len(nums) - 1, target)
        if a != -1: return True
        return False

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

    # # pivot is a[i] > a[i-1] and a[i] > a[i+1]
    # def locate_pivot(self, nums):
    #     (s, e) = (0, len(nums) - 1)

    #     # make sure 3 elements.
    #     while (e - s) >= 2:
    #         # print (s, e)
    #         m = (s + e) / 2
    #         # 100 percent sure.
    #         if ((m - 1) >= 0 and nums[m] > nums[m - 1]) and \
    #             ((m + 1) < len(nums) and nums[m] > nums[m + 1]):
    #              return m

    #         if nums[m] > nums[e]:
    #             s = m
    #         else:
    #             e = m

    #     # special cases.
    #     if (e - s) == 1:
    #         if nums[s] < nums[e]: return e
    #         else: return s
    #     else:
    #         return s

    # TOOD(yan): FIX ME. not O(lgN)
    def locate_pivot(self, nums):
        p = 1
        while p < len(nums):
            if nums[p-1] > nums[p]:
                return p-1
            p += 1
        return len(nums) / 2
