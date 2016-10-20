#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

# class Solution(object):
#     def longestValidParentheses(self, s):
#         """
#         :type s: str
#         :rtype: int
#         """
#         n = len(s)
#         st = [[0] * n, [0] * n]
#         for i in range(0, n):
#             if s[i] == '(':
#                 st[0][i] = 1
#             elif s[i] == ')':
#                 st[0][i] = -1 # broken.

#         sti = 0
#         res = 0

#         for sz in range(2, n + 1):
#             sti = 1 - sti
#             for i in xrange(0, n - sz + 1):
#                 # already broken.
#                 if st[1-sti][i] < 0:
#                     st[sti][i] = -1
#                     continue

#                 if s[i + sz - 1] == '(':
#                     st[sti][i] = st[1-sti][i]+1
#                 elif s[i + sz - 1] == ')':
#                     st[sti][i] = st[1-sti][i]-1

#                 if st[sti][i] == 0:
#                     res = sz
#             # print '-----sz = {}-----'.format(sz)
#             # print st[sti]

#         return res

# class Solution(object):
#     def longestValidParentheses(self, s):
#         """
#         :type s: str
#         :rtype: int
#         """
#         res = 0
#         n = len(s)
#         i = 0
#         while i < n:
#             j = i
#             st = 0
#             while j < n:
#                 if s[j] == '(':
#                     st += 1
#                     if (n - j - 1) < st:
#                         break
#                 else:
#                     st -= 1
#                     if st < 0:
#                         i = j
#                         break
#                 if st == 0: res = max(res, j - i + 1)
#                 j += 1
#             if res >= (n - i):
#                 break
#             i += 1
#         return res

class Solution(object):
    def longestValidParentheses(self, s):
        # s_ = Solution_()
        # print 'correct = ', s_.longestValidParentheses(s)

        """
        :type s: str
        :rtype: int
        """

        # stack based solution. code pretty ugly.

        ss = []
        res = 0

        for c in s:
            if c == '(':
                ss.append('(')
                continue

            if not ss: continue

            p = ss.pop()
            if isinstance(p, int):
                if not ss:
                    res = max(res, p)
                    continue
                value = p
                p = ss.pop()
            else:
                value = 0

            if p == '(':
                value += 1
                while ss:
                    p = ss.pop()
                    if isinstance(p, int):
                        value += p
                    else:
                        ss.append(p)
                        break
                ss.append(value)
            else:
                if value: ss.append(value)
                ss.append(')')

        for c in ss:
            if isinstance(c, int):
                res = max(c, res)
        return res * 2

if __name__ == '__main__':
    s = Solution()
    print s.longestValidParentheses(")()())()()(")
    print s.longestValidParentheses(')()())')
    print s.longestValidParentheses('()()')
    print s.longestValidParentheses('(()')
    print s.longestValidParentheses('()(()')
    print s.longestValidParentheses("(()(((()")
    print s.longestValidParentheses('(())(()))))(((((((()()))())')
    print s.longestValidParentheses("()()()(()))()()())))((()()()(()()))(()()()((()()))())(((())()())(()(()(()(())(((()())()))(()))()))))()())(()))))()()(())()()((())()()))))((()))))(()()((()(()(()())((())()()()()))()()()(())()()())((((()(())())))(((()(((()((((())())(()()()()(((((()))()(()(())))(((()()()()(()(((())(()(()()(()(()(())()))))))()))()())((()((((()(())(()()()(((((()())()))))())))((((()()()(()(())(((())(((()()((()((()(((()(()))(((())(((()((((()(())(((()((()(()())))))(()(()()(())))))()(()()((()))()))())())((())))()(())((((()((()))))()())()))((()(()())()())()()((()))())(()(()(())((((((()()((((())))())(((()()())))()(((()(()()((((())))))()()((((()(()()())(()(())()()()((()(()((((())))((((((())(()())()))))(()(()))()))))))(()()((()()()())(())))(((()))(()()()(()))((())()()()())()()(((())(()(())()()(()())((()()(((((())(()((((()(()()()(()))(()((((())()())()())())))())(((()(()((())()()((((()()()()))))))())())()(((((()())()(()()()()()(((())((((((()))(())()(()())(()(()())(()(())))())))(()()(()((((()()(())(()))()))(()))(()())())()))))))()()(())))))()))()(()())))((())(()()))()((()))()(())()()((((())()))((()(()))()(((()())()(()()((()())((((())()))))()(())())())())(((()(()())))((()))))()())))))(()((())))()())((()))()()))(())())()))()()((()(((())()()()((()()(()(())(()))())())(((()())(()())(()((()()()())()(()(((((((()()(((()(((((((())(()))))())()))))))))()(()(()((((())(()()(((()))()(())(((((((((()(()())())()(((()((()(((()(()()(()))(())))))))(((")
