#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def isPalindrome(self, s):
        """
        :type s: str
        :rtype: bool
        """
        s = map(lambda x: x.lower(), filter(lambda x: x.isalnum(), s))
        return s == s[::-1]
