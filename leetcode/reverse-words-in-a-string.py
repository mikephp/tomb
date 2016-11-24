#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

class Solution(object):
    def reverseWords(self, s):
        """
        :type s: st
        :rtype: str
        """
        ss = filter(lambda x: x, s.split(' '))
        return ' '.join(ss[::-1])
