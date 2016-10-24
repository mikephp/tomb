#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def firstMissingPositive(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        # TODO(yan): FIX ME. not O(N)
        nums = filter(lambda x: x > 0, nums)
        nums.sort()
        if len(nums) == 0: return 1

        exp = 1
        prev = None
        for c in nums:
            if c == prev:
                continue
            else:
                prev = c
                if c != exp:
                    return exp
                exp += 1
        return c + 1

if __name__ == '__main__':
    s = Solution()
    print s.firstMissingPositive([1,2,0])
    print s.firstMissingPositive([3, 4, 1, -1])
    print s.firstMissingPositive([1, 1000])
    print s.firstMissingPositive([1, 2, 1000])
