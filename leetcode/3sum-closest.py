#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def threeSumClosest(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: int
        """
        nums.sort()
        res = None
        for i in range(0, len(nums)):
            (k, j) = (i + 1, len(nums) - 1)
            x = nums[i]
            while k < j:
                y = nums[k]
                z = nums[j]
                _sum = x + y + z
                dist = _sum - target                
                if res is None or abs(res - target) > abs(dist):
                    res = _sum
                if dist == 0: return res
                elif dist > 0: j-=1
                else: k+=1
        return res

if __name__ == '__main__':
    s = Solution()
    print s.threeSumClosest([-1, 2, 1, -4], 1)
