#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def isInterleave(self, s1, s2, s3):
        """
        :type s1: str
        :type s2: str
        :type s3: str
        :rtype: bool
        """
        n = len(s1)
        m = len(s2)
        if n + m != len(s3): return False

        st = []
        for i in range(0, (n + 1)):
            st.append([False] * (m + 1))
        st[0][0] = True
        for i in range(1, m + 1):
            st[0][i] = s2[:i] == s3[:i]
        for i in range(1, n + 1):
            st[i][0] = s1[:i] == s3[:i]

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                st[i][j] = (st[i-1][j] and s1[i-1] == s3[i+j-1]) or \
                  (st[i][j-1] and s2[j-1] == s3[i+j-1])

        # for x in st:
        #     print x
        return st[n][m]

if __name__ == '__main__':
    s = Solution()
    print s.isInterleave('aabcc', 'dbbca', 'aadbbcbcac')
