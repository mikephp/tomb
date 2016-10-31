#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def sortColors(self, nums):
        """
        :type nums: List[int]
        :rtype: void Do not return anything, modify nums in-place instead.
        """
        c = [0, 0, 0]
        for n in nums:
            c[n] += 1
        for i in range(c[0]): nums[i] = 0
        for i in range(c[0], c[0] + c[1]): nums[i] = 1
        for i in range(c[0] + c[1], c[0] + c[1] + c[2]): nums[i] = 2
