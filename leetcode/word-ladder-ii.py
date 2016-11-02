#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def findLadders(self, beginWord, endWord, wordlist):
        """
        :type beginWord: str
        :type endWord: str
        :type wordlist: Set[str]
        :rtype: List[List[int]]
        """
        if beginWord in wordlist:
            wordlist.remove(beginWord)
        if endWord in wordlist:
            wordlist.remove(endWord)
        wordlist = list(wordlist)
        wordlist.insert(0, beginWord)
        wordlist.append(endWord)
        n = len(wordlist)

        tb = []
        G = []
        for i in xrange(n):
            G.append([])
            tb.append([])

        # NOTE(yan): 这里计算G有一些技巧，如果简单地O(n^2)去计算两个word是否相差一个字符的话
        # 是会出现TLE的。我观察到的是，为什么hit和hot是相差一个字符的，是因为如果我们把字符串rotate一下的话
        # 那么就只需要检查除去最后一个字符串是否相同即可：hit -> thi,  hot -> tho.
        # 注意这里需要使用所有的位置来rotate. 好处是一旦rotate完成后，就是线性比较，速度会加快不少。

        # 假设每个字符串长k, n个字符串.
        # 简单比较的时间复杂度是O(n^2 * k)
        # 后面一种时间复杂度是O(nlgn * k * k+ n*k).
        wordlist2 = [(x, idx) for (idx, x) in enumerate(wordlist)]

        def updateG(ws):
            pfx = ws[0][0][:-1]
            pfx_idx = 0

            def fx_range(i, j):
                for x in range(i, j):
                    for y in range(x+1, j):
                        a = ws[x][1]
                        b = ws[y][1]
                        G[a].append(b)
                        G[b].append(a)

            for i in range(1, len(ws)):
                if ws[i][0].startswith(pfx):
                    continue
                fx_range(pfx_idx, i)
                pfx = ws[i][0][:-1]
                pfx_idx = i

            fx_range(pfx_idx, len(ws))

        for off in range(0, len(beginWord)):
            tmp_ws = map(lambda (x, idx): (x[off:] + x[:off], idx), wordlist2)
            tmp_ws.sort(key = lambda x: x[0])
            # print tmp_ws
            updateG(tmp_ws)

        from collections import deque
        Q = deque()
        seen = set()
        Q.append((0, 0))
        seen.add(0)

        while len(Q):
            (v, d) = Q.popleft()
            if v == (n-1):
                break

            v2s = G[v]
            for v2 in v2s:
                tb[v2].append((v, d + 1))
                if v2 not in seen:
                    seen.add(v2)
                    Q.append((v2, d + 1))

        # for i in range(n):
        #     print '{} -> {}'.format(i, tb[i])

        if not tb[n-1]: return []

        min_dist = min(map(lambda x: x[1], tb[n-1]))
        res = []
        def backtrace(idx, dist, r):
            if idx == 0:
                res.append(map(lambda x: wordlist[x], reversed(r)))
                return

            for (v, d) in tb[idx]:
                if d != dist: continue
                if d > dist: break
                r.append(v)
                backtrace(v, dist - 1, r)
                r.pop()
        r = [n-1]
        backtrace(n-1, min_dist, r)
        return res

if __name__ == '__main__':
    s = Solution()
    print s.findLadders('hit', 'cog',  ["hot","dot","dog","lot","log"])
    print s.findLadders('hot', 'dog',  ["hot",'dog'])
    print s.findLadders("lost", "miss", ["most","mist","miss","lost","fist","fish"])
