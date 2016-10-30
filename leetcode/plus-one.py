#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def plusOne(self, digits):
        """
        :type digits: List[int]
        :rtype: List[int]
        """
        f = 1
        for i in range(len(digits) -1 , -1, -1):
            f += digits[i]
            digits[i] = f % 10
            f = f / 10
        if f:
            digits.insert(0, f)
        return digits
