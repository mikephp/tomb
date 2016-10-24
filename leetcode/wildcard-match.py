#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

# class Solution(object):
#     def isMatch(self, s, p):
#         """
#         :type s: str
#         :type p: str
#         :rtype: bool
#         """

#         # to match 'a*' or '.*' against empty string
#         s = '#' + s
#         # add prefix to avoid index error.
#         p = '^' + p
#         st = []
#         for i in range(len(s)):
#             st.append([0] * len(p))
#         self.st = st
#         st[0][0] = 1

#         for i in range(0, len(s)):
#             for j in range(1, len(p)):
#                 def cmatch():
#                     return p[j] == '*' or \
#                       (p[j] == '?' and i != 0) or \
#                       (p[j] == s[i])

#                 if not cmatch():
#                     continue

#                 if (p[j] == '?' and i != 0) or p[j] == s[i]:
#                     st[i][j] = st[i-1][j-1]
#                 else:
#                     for x in range(i, -1, -1):
#                         if st[x][j-1]:
#                             st[i][j] = 1
#                             break

#         return bool(st[len(s)-1][len(p)-1])

# class Solution(object):
#     def isMatch(self, s, p):
#         """
#         :type s: str
#         :type p: str
#         :rtype: bool
#         """

#         # to match 'a*' or '.*' against empty string
#         s = '#' + s
#         # add prefix to avoid index error.
#         p = '^' + p
#         st = []
#         for i in range(len(s)):
#             st.append([0] * len(p))
#         self.st = st
#         st[0][0] = 1

#         for j in range(1, len(p)):
#             if p[j] == '*':
#                 v = 0
#                 for i in range(0, len(s)):
#                     v |= st[i][j-1]
#                     st[i][j] = v

#             else:
#                 for i in range(1, len(s)):
#                     if p[j] == s[i] or p[j] == '?':
#                         st[i][j] = st[i-1][j-1]

#         return bool(st[len(s)-1][len(p)-1])

# class Solution(object):
#     def isMatch(self, s, p):
#         """
#         :type s: str
#         :type p: str
#         :rtype: bool
#         """

#         # to match 'a*' or '.*' against empty string
#         s = '#' + s
#         # add prefix to avoid index error.
#         p = '^' + p
#         st = []
#         for i in range(2):
#             st.append([0] * len(s))
#         self.st = st
#         st[0][0] = 1
#         swt = 0

#         for j in range(1, len(p)):
#             aft = 1 - swt
#             if p[j] == '*':
#                 v = 0
#                 for i in range(0, len(s)):
#                     v |= st[swt][i]
#                     st[aft][i] = v

#             else:
#                 st[1-swt][0] = 0
#                 for i in range(1, len(s)):
#                     if p[j] == s[i] or p[j] == '?':
#                         st[aft][i] = st[swt][i-1]
#                     else:
#                         st[aft][i] = 0
#             swt = 1- swt
#             # print st

#         return bool(st[swt][len(s)-1])

# TODO(yan): case is N >= 5000



if __name__ == '__main__':
    s = Solution()
    print s.isMatch("aa", "*")
    print s.isMatch("aab", "c*a*b")
    print s.isMatch("ab", "?*")
    print s.isMatch("", "?")
    print s.isMatch("b","*?*?")
