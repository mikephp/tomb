#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def lengthOfLongestSubstring(self, s):
        """
        :type s: str
        :rtype: int
        """
        cset = set()
        (i, j, ret) = (0, 0, 0)
        while j < len(s):
            c = s[j]
            while c in cset:
                c2 = s[i]
                cset.remove(c2)
                i += 1
            cset.add(c)
            ret = max(ret, len(cset))
            j += 1
        return ret

if __name__ == '__main__':
    s = Solution()
    print s.lengthOfLongestSubstring('c')
    print s.lengthOfLongestSubstring('')
    print s.lengthOfLongestSubstring("jhhthogonzpheevzetkvygpvbdhcaisjpbfwslmflbopgmqmfcjdkzbmckqeskpjluhditltvzkdlap")
