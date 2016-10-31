#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def removeDuplicates(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        if not nums: return 0
        res = []
        prev = nums[0]
        got_dup = 0
        for i in range(1, len(nums)):
            v = nums[i]
            if v == prev:
                got_dup = 1
                continue
            else:
                res.extend([prev] * (1 + got_dup))
                prev = v
                got_dup = 0
        res.extend([prev] * (1 + got_dup))
        return res

if __name__ == '__main__':
    s = Solution()
    print s.removeDuplicates([1,1,1,2])
    print s.removeDuplicates([1])
