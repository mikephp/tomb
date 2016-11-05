#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def longestConsecutive(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """

        # TODO(yan): FIXME. not in O(n)
        nums.sort()
        if not nums: return 0
        pp = nums[0]
        res = 1
        cnt = 1
        for p in nums[1:]:
            if p not in (pp, pp + 1):
                res = max(res, cnt)
                cnt = 0
            if p == pp:
                cnt -= 1
            cnt += 1
            pp = p
        res = max(res, cnt)
        return res
