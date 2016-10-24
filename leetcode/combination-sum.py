#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def combinationSum(self, candidates, target):
        """
        :type candidates: List[int]
        :type target: int
        :rtype: List[List[int]]
        """
        candidates = filter(lambda x: x <= target, candidates)
        if not candidates: return []
        
        candidates.sort()
        st = []
        for i in range(len(candidates)):
            sub_st = []
            for j in range(0, target + 1):
                sub_st.append([])
            st.append(sub_st)

        a = candidates[0]
        c = 0
        while (a * c) <= target:
            st[0][a * c].append([a] * c)
            c += 1

        for i in range(1, len(candidates)):
            a = candidates[i]
            for t in range(0, target + 1):
                c = 0
                while (a * c) <= t:
                    rest = t - a * c
                    possibles = st[i - 1][rest]
                    for p in possibles:
                        st[i][t].append(p + [a] * c)
                    c += 1

        return st[len(candidates) - 1][target]

if __name__ == '__main__':
    s = Solution()
    print s.combinationSum([2,3,6,7], 7)
