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
    def maxPathSum(self, root):
        """
        :type root: TreeNode
        :rtype: int
        """

        def fx(root):
            if not root: return (- (1 << 30), 0)
            (lpath, ld) = fx(root.left)
            (rpath, rd) = fx(root.right)
            path = max(lpath, rpath, ld + rd + root.val, ld + root.val, rd + root.val, root.val)
            depth = max(ld + root.val, rd + root.val, root.val)
            return (path, depth)

        (res, _) = fx(root)
        return res
