#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def singleNumber(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        x = 0
        for n in nums:
            x = x ^ n
        return x
