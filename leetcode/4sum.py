#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def fourSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[List[int]]
        """

        nums.sort()
        res = []
        # O(n^3)
        for i in range(0, len(nums) - 1):
            for j in range(i + 1, len(nums) - 1):
                (k, l) = (j + 1, len(nums) - 1)
                while k < l:
                    _sum = nums[i] + nums[j] + nums[k] + nums[l]
                    if _sum == target:
                        res.append((nums[i], nums[j], nums[k], nums[l]))
                        k += 1
                    elif _sum > target: l -= 1
                    else: k += 1
        res2 = set(res)
        res = map(list, res2)
        return res

if __name__ == '__main__':
    s = Solution()
    print s.fourSum([1, 0, -1, 0, -2, 2], 0)
