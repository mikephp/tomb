#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def combinationSum2(self, candidates, target):
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
        st[0][a].append([a])
        st[0][0].append([])

        for i in range(1, len(candidates)):
            a = candidates[i]
            for t in range(0, target + 1):
                if not st[i-1][t]: continue
                possibles = st[i-1][t]
                st[i][t].extend(st[i-1][t][:])
                if (t + a) <= target:
                    for p in possibles:
                        st[i][t + a].append(p + [a])

        res = st[len(candidates) - 1][target]
        res = map(list, set(map(tuple, res)))
        return res

if __name__ == '__main__':
    s = Solution()
    print s.combinationSum2([10, 1, 2, 7, 6, 1, 5], 8)
