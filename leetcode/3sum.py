#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def threeSum(self, nums):
        """
        :type nums: List[int]
        :rtype: List[List[int]]
        """
        nums.sort()
        res = []
        for i in range(0, len(nums)):
            a = nums[i]
            def search(x, s, e):
                y = - x
                ss = []
                while s < e:
                    v = nums[s] + nums[e]
                    if v == y:
                        ss.append((x, nums[s], nums[e]))
                        s += 1
                    elif v > y:
                        e -= 1
                    else:
                        s += 1
                return ss
            ss = search(a, i+1, len(nums) - 1)
            res.extend(ss)

        res2 = set(res)
        res = map(list, list(res2))
        return res

if __name__ == '__main__':
    s = Solution()
    print s.threeSum([-1, 0, 1, 2, -1, -4])
