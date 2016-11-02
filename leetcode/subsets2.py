#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def subsetsWithDup(self, nums):
        """
        :type nums: List[int]
        :rtype: List[List[int]]
        """

        from collections import defaultdict
        d = defaultdict(int)
        for n in nums:
            d[n] += 1
        keys = d.keys()

        # res = []
        # def f(idx, r):
        #     if idx == len(keys):
        #         r2 = []
        #         for (k, v) in r:
        #             r2.extend([k] * v)
        #         res.append(r2)
        #         return
        #     k = keys[idx]
        #     v = d[k]
        #     for i in range(0, v + 1):
        #         r.append((k, i))
        #         f(idx + 1, r)
        #         r.pop()

        # r = []
        # f(0, r)

        res = [[]]
        for k in keys:
            res2 = []
            for v in range(0, d[k] + 1):
                for r in res:
                    res2.append([k] * v + r)
            res = res2

        return res
