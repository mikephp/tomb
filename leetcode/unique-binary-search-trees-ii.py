#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

# Definition for a binary tree node.
# class TreeNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution(object):
    def generateTrees(self, n):
        """
        :type n: int
        :rtype: List[TreeNode]
        """

        if n == 0: return []
        st = []
        for i in range(n + 1):
            st.append([])
        st[0].append(None)

        def copy_tree(t, off = 0):
            if not t: return None
            l = copy_tree(t.left, off)
            r = copy_tree(t.right, off)
            x = TreeNode(t.val + off)
            x.left = l
            x.right = r
            return x

        for i in range(1, n + 1):
            for j in range(0, i):
                # j+1 in middle.
                ls = st[j]
                rs = st[i-1-j]
                for l in ls:
                    for r in rs:
                        t = TreeNode(j+1)
                        t.left = l
                        t.right = copy_tree(r, j+1)
                        st[i].append(t)
        return st[n]
